#!/usr/bin/env python3
"""Report added GUI string literals as review evidence, never as full coverage."""
import argparse
import json
from pathlib import Path
import re
import subprocess

LITERAL = re.compile(r'"((?:\\.|[^"\\])*)"')
KEY = re.compile(r'\{\s*"((?:\\.|[^"\\])*)"\s*,\s*"')


def added_literals(diff, catalog):
    keys = set(KEY.findall(catalog))
    path, line, result = '', 0, []
    for text in diff.splitlines():
        if text.startswith('+++ b/'):
            path = text[6:]
        elif match := re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', text):
            line = int(match[1])
        elif text.startswith('+') and not text.startswith('+++'):
            for value in LITERAL.findall(text[1:]):
                if re.search('[A-Za-z]', value):
                    result.append(dict(path=path, line=line, literal=value, exact_catalog_key=value in keys))
            line += 1
        elif text.startswith(' '):
            line += 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before'); parser.add_argument('after')
    parser.add_argument('--source', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for sha in (args.before, args.after):
        if not re.fullmatch('[0-9a-f]{40}', sha): raise ValueError('Expected exact commit SHA')
    diff = subprocess.check_output(['git', '-C', str(args.source), 'diff', '--no-ext-diff', '--no-textconv',
                                    '--unified=0', args.before, args.after, '--', 'src/gui_and_draw'], text=True)
    catalog = (args.source / 'src/gui_and_draw/VSPChinese.cpp').read_text(encoding='utf-8')
    result = dict(schema=1, before=args.before, after=args.after,
                  scope='Added single-line C++ string literals under src/gui_and_draw; includes non-UI identifiers.',
                  limitation='Advisory only: dynamic translations, macros, multiline strings and actual GUI rendering need review.',
                  literals=added_literals(diff, catalog))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Added GUI-area string literal candidates: {len(result["literals"])}; inspect the report before native/GUI acceptance.')


if __name__ == '__main__': main()
