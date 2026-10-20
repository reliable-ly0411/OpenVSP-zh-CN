#!/usr/bin/env python3
"""Source contracts and a focused production-method test seam for opaque labels.

The generated C++ includes actual GroupLayout method bodies, not reimplemented
translation logic. Small FLTK/device doubles record labels and layout calls;
this does not replace a native build or graphical acceptance test.
"""
from pathlib import Path
import argparse
import re
import unittest

from check_translation_catalog import strip_comments

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / 'src/gui_and_draw'


def method(source, name, first_arg):
    code = strip_comments(source)
    match = re.search(r'(?:void|Fl_Box\*)\s+GroupLayout::' + name +
                      r'\(\s*' + first_arg + r'[^)]*\)\s*\{', code)
    if not match:
        raise ValueError('Missing GroupLayout method: ' + name)
    depth = 1
    end = match.end()
    while depth and end < len(code):
        depth += (code[end] == '{') - (code[end] == '}')
        end += 1
    if depth:
        raise ValueError('Unbalanced method body: ' + name)
    return code[match.start():end]


def dynamic_call(source, layout, argument):
    return re.search(r'\b' + layout + r'\.(\w+)\(\s*' + argument + r'\s*\)',
                     strip_comments(source))


def label_output_only():
    # Upstream added output-only table labels in 3.54; retain older behavior.
    version = (ROOT / 'src/cmake/VSP_Version.cmake').read_text(encoding='utf-8')
    minor = int(re.search(r'SET\(\s*VSPVER_MINOR\s+(\d+)\s*\)', version)[1])
    return minor >= 54


def generate(destination):
    """Also accepts pre-fix source, so baseline failure is behavioral, not compile failure."""
    destination.mkdir(parents=True, exist_ok=True)
    header = strip_comments((GUI / 'GroupLayout.h').read_text(encoding='utf-8'))
    source = (GUI / 'GroupLayout.cpp').read_text(encoding='utf-8')
    declarations, definitions = [], []
    for name, arg in [('AddButton', 'TriggerButton&'), ('AddButtonRaw', 'TriggerButton&'),
                      ('AddDividerBox', 'const string&'), ('AddDividerBoxRaw', 'const string&'),
                      ('AddLabel', r'const char\*'), ('AddLabelRaw', r'const char\*')]:
        declaration = re.search(r'(?:void|Fl_Box\*)\s+' + name + r'\(\s*' +
                                arg + r'[^;]+;', header)
        if declaration:
            declarations.append(declaration.group())
            definitions.append(method(source, name, arg))
    component = dynamic_call((GUI / 'ParasiteDragScreen.cpp').read_text(encoding='utf-8'),
                             'm_TableCompNamesLayout', r'm_labels\[index\],\s*label\.c_str\(\s*\)')
    group = dynamic_call((GUI / 'UserParmScreen.cpp').read_text(encoding='utf-8'),
                         'm_AdjustLayout', 'groupName')
    excrescence = dynamic_call((GUI / 'ParasiteDragScreen.cpp').read_text(encoding='utf-8'),
                                'm_TableCompNamesLayout',
                                r'excresRowVec\[i\]\.Label\.c_str\(\s*\),\s*TYPICAL_INPUT_WIDTH \* 2 - 15')
    if not component or not group or not excrescence:
        raise ValueError('Cannot identify the production dynamic-label call sites')
    definitions += [
        'const bool kLabelOutputOnly = ' + str(label_output_only()).lower() + ';',
        'void component_label(GroupLayout& layout, TriggerButton& button, const string& label)\n'
        '{ layout.' + component[1] + '(button, label.c_str()); }',
        'Fl_Box* user_group_label(GroupLayout& layout, const string& label)\n'
        '{ return layout.' + group[1] + '(label); }',
        'void excrescence_label(GroupLayout& layout, const string& label)\n'
        '{ layout.' + excrescence[1] + '(label.c_str(), 145); }',
    ]
    (destination / 'layout_label_declarations.inc').write_text('\n'.join(declarations), encoding='utf-8')
    (destination / 'layout_label_definitions.inc').write_text('\n\n'.join(definitions), encoding='utf-8')


class OpaqueLayoutLabelTests(unittest.TestCase):
    def test_component_label_uses_raw_button(self):
        source = (GUI / 'ParasiteDragScreen.cpp').read_text(encoding='utf-8')
        call = dynamic_call(source, 'm_TableCompNamesLayout',
                            r'm_labels\[index\],\s*label\.c_str\(\s*\)')
        self.assertIsNotNone(call)
        self.assertEqual(call[1], 'AddButtonRaw')
        self.assertIn('GetComponentTableLabel( subsurfFlag, lastID, index )', source)

    def test_user_group_header_uses_raw_divider(self):
        source = (GUI / 'UserParmScreen.cpp').read_text(encoding='utf-8')
        call = dynamic_call(source, 'm_AdjustLayout', 'groupName')
        self.assertIsNotNone(call)
        self.assertEqual(call[1], 'AddDividerBoxRaw')
        self.assertIn('string groupName = p->GetDisplayGroupName();', source)
        self.assertIn('m_PredefGroup.AddDividerBox( "Predefined" );', source)

    def test_excrescence_name_uses_raw_label(self):
        source = (GUI / 'ParasiteDragScreen.cpp').read_text(encoding='utf-8')
        call = dynamic_call(source, 'm_TableCompNamesLayout',
                            r'excresRowVec\[i\]\.Label\.c_str\(\s*\),\s*TYPICAL_INPUT_WIDTH \* 2 - 15')
        self.assertIsNotNone(call)
        self.assertEqual(call[1], 'AddLabelRaw')
        self.assertIn('AddLabel( "Excrescence"', source)

    def test_raw_helpers_copy_without_translation(self):
        source = (GUI / 'GroupLayout.cpp').read_text(encoding='utf-8')
        for name, arg, value in [('AddButtonRaw', 'TriggerButton&', 'label'),
                                 ('AddDividerBoxRaw', 'const string&', r'text\.c_str\(\s*\)'),
                                 ('AddLabelRaw', r'const char\*', 'label')]:
            body = method(source, name, arg)
            self.assertRegex(body, r'copy_label\(\s*' + value + r'\s*\)')
            self.assertNotRegex(body, r'\bVSPTranslate\w*\s*\(')
            self.assertIn('m_Group->add(', body)
            if name == 'AddLabelRaw':
                self.assertEqual('set_output();' in body, label_output_only())
                self.assertNotIn('NewLineX();', body)
            else:
                self.assertIn('NewLineX();', body)

    def test_static_helpers_translate_once_before_raw_construction(self):
        source = (GUI / 'GroupLayout.cpp').read_text(encoding='utf-8')
        for name, arg, value in [('AddButton', 'TriggerButton&', 'label'),
                                 ('AddDividerBox', 'const string&', 'text'),
                                 ('AddLabel', r'const char\*', 'label')]:
            body = method(source, name, arg)
            self.assertEqual(body.count('VSPTranslate('), 1)
            self.assertIn(name + 'Raw(', body)
            self.assertRegex(body, r'VSPTranslate\(\s*' + value + r'\s*\)')

    def test_callsite_guards_ignore_comments(self):
        for text in ['// m_AdjustLayout.AddDividerBoxRaw( groupName );',
                     '/* m_AdjustLayout.AddDividerBoxRaw( groupName ); */']:
            self.assertIsNone(dynamic_call(text, 'm_AdjustLayout', 'groupName'))
        wrong = dynamic_call('m_AdjustLayout.AddDividerBox(groupName);', 'm_AdjustLayout', 'groupName')
        self.assertNotEqual(wrong[1], 'AddDividerBoxRaw')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', type=Path)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    args, rest = parser.parse_known_args()
    ROOT = args.source_root
    GUI = ROOT / 'src/gui_and_draw'
    if args.generate:
        generate(args.generate)
    else:
        unittest.main(argv=[__file__] + rest)
