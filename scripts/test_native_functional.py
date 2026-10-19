"""Offline STL/results contracts. Fixtures are inert; no native solver executes."""
import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest

from native_functional import (CLI_BASENAME, CLI_HISTORY_FIELDS, CLI_INPUT_SUFFIXES,
                               COMPGEOM_FILENAME, HISTORY_FILENAME, STL_FILENAME,
                               FunctionalCheckError, validate_functional_summary,
                               validate_stl, verify_cli_history, verify_functional_outputs)


ASCII_STL = b'''solid fixture
facet normal 0 0 1
outer loop
vertex 0 0 0
vertex 1 0 0
vertex 0 1 0
endloop
endfacet
endsolid fixture
'''


def binary_stl(values=(0., 0., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0.)):
    # A legal binary header can start with solid and must not be parsed as ASCII.
    return b'solid binary'.ljust(80, b'\0') + struct.pack('<I12fH', 1, *values, 0)


def write_outputs(directory, lift='CLtot,0.1,0.4\n'):
    (directory / STL_FILENAME).write_bytes(ASCII_STL)
    (directory / COMPGEOM_FILENAME).write_text('Results_Name,Comp_Geom\nWet_Area,2.0,3.0\n', encoding='utf-8')
    (directory / HISTORY_FILENAME).write_text('Results_Name,VSPAERO_History\n' + lift, encoding='utf-8')
    for suffix in CLI_INPUT_SUFFIXES:
        (directory / (CLI_BASENAME + suffix)).write_bytes(b'inert solver input')
    # This API-run result must never be copied into the direct CLI scratch dir.
    write_cli_history(directory)


def write_cli_history(directory, rows=None):
    if rows is None:
        rows = [[1.0] * len(CLI_HISTORY_FIELDS), [2.0] * len(CLI_HISTORY_FIELDS)]
        for row in rows:
            row[1:4] = [0.1, 5.0, 0.0]
            row[6] = 0.4
    header = ' '.join(CLI_HISTORY_FIELDS).replace('L2_Residual', 'L2 Residual').replace('Max_Residual', 'Max Residual')
    path = directory / (CLI_BASENAME + '.history')
    path.write_text('Solver Case: 1\n\n' + header + '\n' +
                    '\n'.join(' '.join(map(str, row)) for row in rows) + '\n')
    return path


def cli_summary():
    return dict(exit_code=0, lift_field='CLtot', samples=2, finite_lift=True,
                finite_physical_values=True, residual_semantics_verified=True,
                final_lift_nonzero=True, history_fresh=True)


def functional_summary(include_cli=True):
    result = dict(schema=1, script_origin='pinned workflow tooling',
                stl=dict(unicode_filename=True, format='ascii', triangles=1,
                         finite_coordinates=True, nondegenerate_geometry=True),
                compgeom=dict(regions=2, finite_positive_areas=True),
                vspaero_api=dict(lift_field='CLtot', samples=2, finite_lift=True, final_lift_nonzero=True),
                names_preserved=True, api_errors=0)
    if include_cli:
        result['vspaero_cli'] = cli_summary()
    return result


class FunctionalFilesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        write_outputs(self.root)

    def test_ascii_export_compgeom_and_lift_are_read_only_and_value_free(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = verify_functional_outputs(self.root)
        self.assertEqual(result, functional_summary(include_cli=False))
        validate_functional_summary(dict(result, vspaero_cli=cli_summary()))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        report = json.dumps(result)
        self.assertNotIn(STL_FILENAME, report)
        self.assertNotIn('0.4', report)

    def test_binary_stl_and_cl_compatibility_are_supported(self):
        (self.root / STL_FILENAME).write_bytes(binary_stl())
        (self.root / HISTORY_FILENAME).write_text('Results_Name,VSPAERO_History\nCL,-0.2,-0.3\n')
        result = verify_functional_outputs(self.root)
        self.assertEqual(result['stl']['format'], 'binary')
        self.assertEqual(result['vspaero_api']['lift_field'], 'CL')

    def test_missing_outputs_are_mandatory(self):
        for filename in (STL_FILENAME, COMPGEOM_FILENAME, HISTORY_FILENAME):
            with self.subTest(filename=filename):
                path = self.root / filename; data = path.read_bytes(); path.unlink()
                with self.assertRaises(FunctionalCheckError): verify_functional_outputs(self.root)
                path.write_bytes(data)

    def test_mojibake_filename_and_symlink_do_not_count_as_unicode_export(self):
        original = self.root / STL_FILENAME
        wrong = self.root / 'Export 100% ??.stl'
        original.rename(wrong)
        with self.assertRaisesRegex(FunctionalCheckError, 'stl-file-missing'):
            verify_functional_outputs(self.root)
        original.symlink_to(wrong)
        with self.assertRaisesRegex(FunctionalCheckError, 'stl-file-missing'):
            verify_functional_outputs(self.root)

    def test_empty_truncated_or_malformed_ascii_stl_is_rejected(self):
        for data in (b'', b'solid\nendsolid\n', ASCII_STL[:-25],
                     ASCII_STL.replace(b'vertex 0 1 0\n', b''),
                     ASCII_STL.replace(b'endloop', b'garbage'), ASCII_STL + b'garbage\n'):
            with self.subTest(data=data), self.assertRaises(FunctionalCheckError): validate_stl(data)

    def test_empty_truncated_or_wrong_count_binary_stl_is_rejected(self):
        binary = binary_stl()
        for data in (binary[:-1], binary + b'x', binary[:80] + struct.pack('<I', 0) + binary[84:],
                     binary[:80] + struct.pack('<I', 2) + binary[84:]):
            with self.subTest(size=len(data)), self.assertRaises(FunctionalCheckError): validate_stl(data)

    def test_nonfinite_ascii_normals_and_coordinates_fail(self):
        for value in (b'nan', b'NaN', b'inf', b'-Infinity', b'1e999'):
            for prefix in (b'normal 0', b'vertex 0'):
                with self.subTest(value=value, prefix=prefix), self.assertRaisesRegex(FunctionalCheckError, 'stl-nonfinite'):
                    validate_stl(ASCII_STL.replace(prefix, prefix[:-1] + value, 1))

    def test_nonfinite_binary_normals_and_coordinates_fail(self):
        for position in (0, 3, 11):
            for value in (float('nan'), float('inf'), -float('inf')):
                values = [0., 0., 1., 0., 0., 0., 1., 0., 0., 0., 1., 0.]
                values[position] = value
                with self.subTest(position=position, value=value), self.assertRaisesRegex(FunctionalCheckError, 'stl-nonfinite'):
                    validate_stl(binary_stl(values))

    def test_mesh_with_no_nondegenerate_triangle_fails(self):
        with self.assertRaisesRegex(FunctionalCheckError, 'stl-degenerate'):
            validate_stl(binary_stl([0.] * 12))

    def test_collinear_nonzero_vertices_do_not_gain_area_from_position_scaling(self):
        for points in ((1, 3, 0, 2, 5, 0, 3, 7, 0), (10, 21, 0, 11, 23, 0, 12, 25, 0)):
            binary = binary_stl((0, 0, 1) + points)
            ascii_data = ('solid\nfacet normal 0 0 1\nouter loop\n' +
                          ''.join('vertex %s %s %s\n' % points[i:i + 3] for i in (0, 3, 6)) +
                          'endloop\nendfacet\nendsolid\n').encode()
            for data in (binary, ascii_data):
                with self.subTest(points=points), self.assertRaisesRegex(FunctionalCheckError, 'stl-degenerate'):
                    validate_stl(data)

    def test_compgeom_requires_two_positive_finite_areas(self):
        for row in ('Wet_Area', 'Wet_Area,2', 'Wet_Area,2,3,4', 'Wet_Area,0,3',
                    'Wet_Area,nan,3', 'Wet_Area,inf,3', 'Wet_Area,private-value,3',
                    'Wet_Area,2,3\nWet_Area,2,3'):
            (self.root / COMPGEOM_FILENAME).write_text('Results_Name,Comp_Geom\n' + row + '\n')
            with self.subTest(row=row), self.assertRaises(FunctionalCheckError) as caught:
                verify_functional_outputs(self.root)
            self.assertNotIn('private-value', str(caught.exception))

    def test_lift_requires_one_nonempty_numeric_history_and_final_nonzero(self):
        for row in ('', 'CLtot', 'CLtot,', 'CLtot,private-value', 'CLtot,0.3,0',
                    'CLtot,0.3,0.000001', 'CLtot,0.3,-0.000001',
                    'CLtot,0.2,0.4\nCLtot,0.5', 'CL,0.2\nCL,0.4'):
            (self.root / HISTORY_FILENAME).write_text('Results_Name,VSPAERO_History\n' + row + '\n')
            with self.subTest(row=row), self.assertRaises(FunctionalCheckError) as caught:
                verify_functional_outputs(self.root)
            self.assertNotIn('private-value', str(caught.exception))

    def test_every_lift_sample_must_be_finite(self):
        for row in ('CLtot,nan,0.4', 'CLtot,0.2,Infinity', 'CLtot,-Infinity,0.3', 'CLtot,1e999,0.3'):
            (self.root / HISTORY_FILENAME).write_text('Results_Name,VSPAERO_History\n' + row + '\n')
            with self.subTest(row=row), self.assertRaisesRegex(FunctionalCheckError, 'history-lift-nonfinite'):
                verify_functional_outputs(self.root)

    def test_invalid_cltot_cannot_fall_back_to_valid_cl(self):
        for row in ('CLtot\nCL,0.4', 'CLtot,nan\nCL,0.4', 'CLtot,0\nCL,0.4'):
            (self.root / HISTORY_FILENAME).write_text('Results_Name,VSPAERO_History\n' + row + '\n')
            with self.subTest(row=row), self.assertRaises(FunctionalCheckError): verify_functional_outputs(self.root)

    def test_wrong_result_header_or_extra_result_section_fails(self):
        for name, result in ((COMPGEOM_FILENAME, 'Comp_Geom'), (HISTORY_FILENAME, 'VSPAERO_History')):
            path = self.root / name; original = path.read_bytes()
            for bad in (original.replace(result.encode(), b'Wrong_Result'),
                        original + b'Results_Name,Extra_Result\n', b'"unterminated'):
                path.write_bytes(bad)
                with self.subTest(name=name), self.assertRaises(FunctionalCheckError): verify_functional_outputs(self.root)
            path.write_bytes(original)

    def test_summary_cannot_omit_or_falsify_required_functional_evidence(self):
        invalid = [None, {}, dict(functional_summary(), api_errors=True),
                   dict(functional_summary(), schema=True), dict(functional_summary(), schema=1.0)]
        for section, field, value in (('stl', 'triangles', 0), ('stl', 'triangles', True),
                                      ('stl', 'unicode_filename', False), ('stl', 'finite_coordinates', False),
                                      ('compgeom', 'regions', 1), ('vspaero_api', 'samples', 0),
                                      ('vspaero_api', 'final_lift_nonzero', False), ('vspaero_api', 'finite_lift', False),
                                      ('vspaero_cli', 'exit_code', 1), ('vspaero_cli', 'exit_code', False),
                                      ('vspaero_cli', 'history_fresh', False), ('vspaero_cli', 'finite_lift', False)):
            changed = copy.deepcopy(functional_summary()); changed[section][field] = value; invalid.append(changed)
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError): validate_functional_summary(value)

    def test_direct_cli_history_has_complete_finite_nonzero_lift_results(self):
        result = verify_cli_history(self.root)
        self.assertEqual(dict(result, exit_code=0), cli_summary())

    def test_direct_cli_missing_empty_truncated_duplicate_or_wrong_history_fails(self):
        path = self.root / (CLI_BASENAME + '.history'); original = path.read_text()
        path.unlink()
        with self.assertRaises(FunctionalCheckError): verify_cli_history(self.root)
        for data in ('', 'Done\n', original + original, original.rsplit(' ', 1)[0],
                     original.replace('CLtot', 'CL'), original.replace('L2 Residual', 'Unexpected')):
            path.write_text(data)
            with self.subTest(data=data[:10]), self.assertRaises(FunctionalCheckError): verify_cli_history(self.root)

    def test_direct_cli_nonfinite_lift_and_physical_values_or_final_zero_fail(self):
        for index in (0, 1, 6, 12, 50):
            for bad in (float('nan'), float('inf'), -float('inf')):
                rows = [[1.] * len(CLI_HISTORY_FIELDS), [2.] * len(CLI_HISTORY_FIELDS)]
                rows[0][index] = bad
                write_cli_history(self.root, rows)
                with self.subTest(index=index, bad=bad), self.assertRaisesRegex(FunctionalCheckError, 'cli-history-nonfinite'):
                    verify_cli_history(self.root)
        for value in (0., 1e-6, -1e-6):
            rows = [[1.] * len(CLI_HISTORY_FIELDS)]; rows[-1][6] = value
            write_cli_history(self.root, rows)
            with self.assertRaisesRegex(FunctionalCheckError, 'cli-history-lift-zero'): verify_cli_history(self.root)

    def test_only_log_zero_residuals_may_be_negative_infinity(self):
        for column in ('L2_Residual', 'Max_Residual'):
            rows = [[1.] * len(CLI_HISTORY_FIELDS)]
            index = CLI_HISTORY_FIELDS.index(column)
            rows[0][index] = -float('inf'); write_cli_history(self.root, rows)
            self.assertTrue(verify_cli_history(self.root)['residual_semantics_verified'])
            for bad in (float('nan'), float('inf')):
                rows[0][index] = bad; write_cli_history(self.root, rows)
                with self.assertRaisesRegex(FunctionalCheckError, 'cli-history-nonfinite'): verify_cli_history(self.root)

    def test_script_preserves_shared_documented_api_and_nonzero_solver_contract(self):
        script = (Path(__file__).parent / 'native_functional_smoke.as').read_text(encoding='utf-8')
        for text in ('ExportFile("Export 100% 中文.stl", SET_ALL, EXPORT_STL)',
                     'ComputeCompGeom(SET_ALL, false, 0)', 'ExecAnalysis(analysis)',
                     'SetIntAnalysisInput(analysis, "NCPU", one)',
                     'WriteResultsCSVFile(comp, "native-compgeom.csv")',
                     'WriteResultsCSVFile(history, "native-vspaero-history.csv")',
                     'abs(lift[lift.length() - 1]) > 1e-6', 'GetNumTotalErrors()',
                     'GetGeomName(pod) != "Export_100%_用户"', 'GetGeomName(wing) != "SolverWing_用户"'):
            self.assertIn(text, script)


if __name__ == '__main__':
    unittest.main()
