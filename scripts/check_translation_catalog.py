#!/usr/bin/env python3
"""Validate display translations without running the GUI or changing model data.

Checks exact/phrase table uniqueness and agreement, reviewed complete-label
regressions, protected formats, View menu context, every static browser heading,
and literal labels at common GUI entry points. This is a source-level guard, not
an AST-complete GUI or terminology acceptance test. Dynamic strings, parameter
explanations, and third-party widgets still require separate review.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / "src/gui_and_draw"
TESTS = ROOT / "scripts/localization_tests"
STRING = r'"(?:\\.|[^"\\])*"'
ENTRY = re.compile(r'\{\s*(' + STRING + r')\s*,\s*(' + STRING + r')\s*\}')
COMMENTS_OR_STRINGS = re.compile(STRING + r'|//[^\n]*|/\*[\s\S]*?\*/')
CALLS = (
    "Alert|fl_alert|fl_message|AddItem|SetTitle|AddTab|AddButton|AddDividerBox|"
    "AddLabel|AddSlider|AddInput|AddOutput|AddChoice|MakeTab|add"
)
LABEL = re.compile(r'\b(?:' + CALLS + r')\s*\([^;"\n]*(' + STRING + r')')
FORMAT = re.compile(r'%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diouxXeEfFgGaAcspn%]')
CJK = re.compile(r'[\u3400-\u9fff]')


def strip_comments(source):
    return COMMENTS_OR_STRINGS.sub(
        lambda match: match[0] if match[0].startswith('"') else '\n' * match[0].count('\n'),
        source,
    )


def read_catalogs(source):
    tables = {}
    errors = []
    for name in ("ExactTranslations", "PhraseTranslations"):
        start = source.find(name + "()")
        if start < 0:
            errors.append(f"Missing translation table: {name}")
            continue
        end = source.index('\n}', start)
        rows = [(json.loads(k), json.loads(v)) for k, v in ENTRY.findall(source[start:end])]
        counts = Counter(key for key, value in rows)
        errors.extend(f"{name}: duplicate key {key!r} ({count} entries)"
                      for key, count in counts.items() if count > 1)
        tables[name] = dict(rows)
    if len(tables) == 2:
        exact, phrase = tables["ExactTranslations"], tables["PhraseTranslations"]
        errors.extend(f"Conflicting exact/phrase translation: {key!r}"
                      for key in exact.keys() & phrase.keys() if exact[key] != phrase[key])
    return tables, errors


def has_unconditional_translation_include(source):
    """Require header users to declare the helper on every build platform."""
    depth = 0
    for line in strip_comments(source).splitlines():
        directive = re.match(r'\s*#\s*(if|ifdef|ifndef|endif|include)\b(.*)', line)
        if not directive:
            continue
        kind, value = directive.groups()
        if kind in ("if", "ifdef", "ifndef"):
            depth += 1
        elif kind == "endif":
            depth = max(0, depth - 1)
        elif depth == 0 and value.strip() == '"VSPChinese.h"':
            return True
    return False


def extract_labels(source):
    labels = set()
    for match in LABEL.finditer(strip_comments(source)):
        label = json.loads(match[1])
        if not re.search('[A-Za-z]', label) or CJK.search(label) or label.startswith('@'):
            continue
        # A variable label followed by a numeric format can be captured by the
        # conservative scanner; bare printf strings are not natural-language UI.
        if not FORMAT.sub('', label).strip():
            continue
        labels.add(label)
    return labels


def translate(driver, labels, mode="translate"):
    if not labels:
        return []
    process = subprocess.run(
        [str(driver), mode], input=('\0'.join(labels) + '\0').encode('utf-8'),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    output = process.stdout.decode('utf-8').split('\0')
    if len(output) != len(labels) + 1 or output[-1] != '':
        raise ValueError("Translation driver returned invalid NUL framing")
    return output[:-1]


def run(driver):
    source = (GUI / "VSPChinese.cpp").read_text(encoding='utf-8')
    tables, errors = read_catalogs(source)
    known = {key for table in tables.values() for key in table}
    expected = json.loads((TESTS / "catalog_cases.json").read_text(encoding='utf-8'))
    preserved = json.loads((TESTS / "catalog_preserved.json").read_text(encoding='utf-8'))
    errors.extend(f"Unexplained preserved label: {key!r}" for key, why in preserved.items() if not why.strip())
    errors.extend(f"Preserved label also has a changing translation: {key!r}"
                  for key in preserved for table in tables.values()
                  if key in table and table[key] != key)
    for label, actual in zip(expected, translate(driver, list(expected))):
        if actual != expected[label]:
            errors.append(f"Translation regression: {label!r} -> {actual!r}; expected {expected[label]!r}")
    for label, actual in zip(preserved, translate(driver, list(preserved))):
        if actual != label:
            errors.append(f"Protected technical label changed: {label!r} -> {actual!r}")

    # Ordinary unknown phrases and data-like text must not become word salad.
    protected = [
        "%s:%6.4f:%s", "%.3f", "%zu", "%1$s", "%%", "*.{pts,csv}",
        "Unknown %s format", "Unknown export *.csv", "@2<<", "@2> Wing",
        "Power Law Unknown Formula", "Unknown Mesh Control", "UnknownWind_7",
        "Mass units used to specify point mass", "Type of end cap on fuselage tail",
    ]
    for label, actual in zip(protected, translate(driver, protected)):
        if actual != label:
            errors.append(f"Unsafe fallback: {label!r} -> {actual!r}")
    directions = {"Top": "顶视图", "Bottom": "底视图", "Left": "左视图", "Right": "右视图",
                  "Front": "前视图", "Rear": "后视图", "Center": "居中"}
    menu_cases = {"File/Open...": "文件/打开...", "View/Top": "视图/顶视图"}
    menu_cases.update({"View/" + key: "视图/" + value for key, value in directions.items()})
    menu_cases.update({"Model/" + key: "模型/" + expected[key] for key in directions})
    for label, actual in zip(menu_cases, translate(driver, list(menu_cases), "menu")):
        if actual != menu_cases[label]:
            errors.append(f"Menu context regression: {label!r} -> {actual!r}")

    labels = {}
    headers = set()
    for path in sorted(GUI.glob('*.cpp')):
        if path.name == "VSPChinese.cpp":
            continue
        contents = path.read_text(encoding='utf-8')
        if (re.search(r'\bVSPTranslateBrowserHeader\s*\(', strip_comments(contents))
                and not has_unconditional_translation_include(contents)):
            errors.append(f"Browser header helper lacks unconditional VSPChinese.h include: {path.name}")
        for label in extract_labels(contents):
            labels.setdefault(label, []).append(path.name)
        headers.update(json.loads(literal) for literal in re.findall(STRING, strip_comments(contents))
                       if literal.startswith('"@b@.'))
    for label in sorted(labels.keys() - known - preserved.keys()):
        errors.append(f"Unreviewed GUI label in {', '.join(labels[label])}: {label!r}")

    header_symbols = {"V/C", "RPM", "CP", "CT", "T", "J", "eta", "X", "Y", "Z", "U", "W"}
    for label, actual in zip(sorted(headers), translate(driver, sorted(headers), 'header')):
        if re.findall(r'[:|]', label) != re.findall(r'[:|]', actual):
            errors.append(f"Changed browser delimiters: {label!r}")
        if re.findall(r'@[^@:.|]*', label) != re.findall(r'@[^@:.|]*', actual):
            errors.append(f"Changed browser formatting: {label!r}")
        for field in re.split('[:|]', actual):
            text = re.sub(r'^@b@(?:c@)?\.', '', field)
            if re.search('[A-Za-z]', text) and text not in header_symbols and not CJK.search(text):
                errors.append(f"Untranslated browser heading: {text!r} in {label!r}")
    header_protected = ["@2<<", "@b@.Unknown", "@@b@.NAME", "NAME:TYPE", "Wing:User Wing",
                        "@b@.NAME@C1", "@b@.用户名称:@b@.RPM"]
    for label, actual in zip(header_protected, translate(driver, header_protected, 'header')):
        if actual != label:
            errors.append(f"Unexpected header parsing: {label!r} -> {actual!r}")
    for label, actual in zip(sorted(headers), translate(driver, sorted(headers))):
        if actual != label:
            errors.append(f"General translator modified browser formatting: {label!r}")

    if errors:
        raise SystemExit('\n'.join(errors))
    print(f"Translation catalog passed: {len(expected)} reviewed cases, {len(preserved)} protected labels, "
          f"{len(labels)} scanned GUI literals, {len(headers)} browser headers.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--driver', type=Path, required=True)
    args = parser.parse_args()
    run(args.driver.resolve())


if __name__ == '__main__':
    main()
