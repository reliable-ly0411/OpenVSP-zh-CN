"""Read-only, value-free validation of the pinned native functional smoke outputs."""
import csv
import io
import math
from pathlib import Path
import re
import struct


FUNCTIONAL_SCRIPT = 'native_functional_smoke.as'
STL_FILENAME = 'Export 100% 中文.stl'
COMPGEOM_FILENAME = 'native-compgeom.csv'
HISTORY_FILENAME = 'native-vspaero-history.csv'
CLI_BASENAME = 'native-analysis'
CLI_INPUT_SUFFIXES = ('.vspaero', '.vspgeom', '.vkey')
CLI_HISTORY_FIELDS = tuple(('Iter Mach AoA Beta CLo CLi CLtot CDo CDi CDtot CSo CSi CStot '
    'L/D E CMox CMoy CMoz CMix CMiy CMiz CMxtot CMytot CMztot CFox CFoy CFoz CFix CFiy CFiz '
    'CFxtot CFytot CFztot CLwtot CDwtot CSwtot CLiw CDiw CSiw CFwxtot CFwytot CFwztot '
    'CFiwx CFiwy CFiwz LoDw Ew T/QS L2_Residual Max_Residual Wall_Time').split())
PASS_MARKERS = ('NATIVE_EXPORT_COMPGEOM_PASS', 'NATIVE_VSPAERO_PASS', 'NATIVE_FUNCTIONAL_PASS')
FAILURE_REASONS = (
    'compgeom_result', 'compgeom_area', 'names', 'export_api', 'vspaero_geometry',
    'vspaero_result', 'vspaero_lift_field', 'vspaero_lift_empty',
    'vspaero_lift_nonfinite', 'vspaero_lift_zero', 'vspaero_api',
)
DISK_FAILURE_REASONS = (
    'workspace-not-fresh', 'stl-file-missing', 'stl-file-invalid', 'stl-nonfinite',
    'stl-degenerate', 'compgeom-file-missing', 'compgeom-file-invalid',
    'compgeom-result-invalid', 'history-file-missing', 'history-file-invalid',
    'history-result-invalid', 'history-lift-nonfinite', 'history-lift-zero',
    'cli-workspace-not-fresh', 'cli-input-file-missing', 'cli-input-file-invalid',
    'cli-history-file-missing', 'cli-history-file-invalid', 'cli-history-result-invalid',
    'cli-history-nonfinite', 'cli-history-lift-zero',
)


class FunctionalCheckError(ValueError):
    """Only fixed categories may leave the private scratch directory."""

    def __init__(self, category):
        if category not in DISK_FAILURE_REASONS:
            raise ValueError('Unknown functional failure category')
        self.category = category
        super().__init__(category)


def read_output(directory, filename, kind, limit):
    path = Path(directory) / filename
    # Exact Unicode directory lookup catches Windows UTF-8/ACP mojibake, even if
    # the executable can reopen its own wrongly encoded name using the same bytes.
    if path.is_symlink() or not path.is_file():
        raise FunctionalCheckError(kind + '-file-missing')
    try:
        if not 0 < path.stat().st_size <= limit:
            raise FunctionalCheckError(kind + '-file-invalid')
        return path.read_bytes()
    except OSError:
        raise FunctionalCheckError(kind + '-file-invalid') from None


def nondegenerate(vertices):
    # Normalize edge vectors, not absolute positions: independently rounded
    # positions can turn exactly collinear vertices into a spurious tiny area.
    a, b, c = vertices
    u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
    if not all(math.isfinite(value) for value in u + v):
        scale = max(abs(value) for vertex in vertices for value in vertex)
        a, b, c = [tuple(value / scale for value in vertex) for vertex in vertices]
        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
    uscale, vscale = max(map(abs, u)), max(map(abs, v))
    if not uscale or not vscale:
        return False
    u, v = [value / uscale for value in u], [value / vscale for value in v]
    return any(abs(u[i] * v[j] - u[j] * v[i]) > 1e-12 for i, j in ((0, 1), (1, 2), (2, 0)))


def validate_stl(data):
    triangles, has_area = 0, False
    # A binary STL header may itself begin with "solid". Its exact size/count
    # contract takes precedence over the ASCII grammar.
    count = struct.unpack_from('<I', data, 80)[0] if len(data) >= 84 else 0
    if count and len(data) == 84 + 50 * count:
        for offset in range(84, len(data), 50):
            values = struct.unpack_from('<12fH', data, offset)[:12]
            if not all(math.isfinite(value) for value in values):
                raise FunctionalCheckError('stl-nonfinite')
            has_area = has_area or nondegenerate([values[i:i + 3] for i in (3, 6, 9)])
        triangles, format_name = count, 'binary'
    else:
        try:
            lines = [line.split() for line in data.decode('utf-8').splitlines() if line.strip()]
        except UnicodeError:
            raise FunctionalCheckError('stl-file-invalid') from None
        position = 0

        def take():
            nonlocal position
            if position >= len(lines):
                raise FunctionalCheckError('stl-file-invalid')
            row = lines[position]; position += 1
            return row

        def vector(prefix):
            row = take()
            if row[:len(prefix)] != prefix or len(row) != len(prefix) + 3:
                raise FunctionalCheckError('stl-file-invalid')
            try:
                values = tuple(float(value) for value in row[len(prefix):])
            except ValueError:
                raise FunctionalCheckError('stl-file-invalid') from None
            if not all(math.isfinite(value) for value in values):
                raise FunctionalCheckError('stl-nonfinite')
            return values

        while position < len(lines):
            if take()[0] != 'solid':
                raise FunctionalCheckError('stl-file-invalid')
            while position < len(lines) and lines[position][0] == 'facet':
                vector(['facet', 'normal'])
                if take() != ['outer', 'loop']:
                    raise FunctionalCheckError('stl-file-invalid')
                vertices = [vector(['vertex']) for _ in range(3)]
                if take() != ['endloop'] or take() != ['endfacet']:
                    raise FunctionalCheckError('stl-file-invalid')
                triangles += 1
                has_area = has_area or nondegenerate(vertices)
            if take()[0] != 'endsolid':
                raise FunctionalCheckError('stl-file-invalid')
        format_name = 'ascii'
    if not triangles:
        raise FunctionalCheckError('stl-file-invalid')
    if not has_area:
        raise FunctionalCheckError('stl-degenerate')
    return dict(unicode_filename=True, format=format_name, triangles=triangles,
                finite_coordinates=True, nondegenerate_geometry=True)


def result_rows(data, expected, kind):
    try:
        rows = list(csv.reader(io.StringIO(data.decode('utf-8')), strict=True))
    except (UnicodeError, csv.Error):
        raise FunctionalCheckError(kind + '-file-invalid') from None
    if (not rows or rows[0] != ['Results_Name', expected]
            or sum(bool(row) and row[0] == 'Results_Name' for row in rows) != 1):
        raise FunctionalCheckError(kind + '-file-invalid')
    return rows


def numeric_row(rows, name, kind):
    matches = [row[1:] for row in rows if row and row[0] == name]
    if len(matches) != 1 or not matches[0]:
        raise FunctionalCheckError(kind + '-result-invalid')
    try:
        return [float(value) for value in matches[0]]
    except ValueError:
        raise FunctionalCheckError(kind + '-result-invalid') from None


def verify_functional_outputs(directory):
    stl = validate_stl(read_output(directory, STL_FILENAME, 'stl', 32 * 1024 * 1024))
    comp = result_rows(read_output(directory, COMPGEOM_FILENAME, 'compgeom', 1024 * 1024),
                       'Comp_Geom', 'compgeom')
    area = numeric_row(comp, 'Wet_Area', 'compgeom')
    if len(area) != 2 or not all(math.isfinite(value) and value > 0 for value in area):
        raise FunctionalCheckError('compgeom-result-invalid')
    history = result_rows(read_output(directory, HISTORY_FILENAME, 'history', 4 * 1024 * 1024),
                          'VSPAERO_History', 'history')
    # Older documented APIs can expose CL. Never hide malformed CLtot by falling
    # back to CL; duplicate lift fields are ambiguous and must also fail.
    for field in ('CLtot', 'CL'):
        if sum(bool(row) and row[0] == field for row in history) > 1:
            raise FunctionalCheckError('history-result-invalid')
    lift_field = 'CLtot' if any(row and row[0] == 'CLtot' for row in history) else 'CL'
    lift = numeric_row(history, lift_field, 'history')
    if not all(math.isfinite(value) for value in lift):
        raise FunctionalCheckError('history-lift-nonfinite')
    if abs(lift[-1]) <= 1e-6:
        raise FunctionalCheckError('history-lift-zero')
    return dict(schema=1, script_origin='pinned workflow tooling', stl=stl,
                compgeom=dict(regions=len(area), finite_positive_areas=True),
                vspaero_api=dict(lift_field=lift_field, samples=len(lift), finite_lift=True,
                                 final_lift_nonzero=True), names_preserved=True, api_errors=0)


def verify_cli_history(directory):
    data = read_output(directory, CLI_BASENAME + '.history', 'cli-history', 4 * 1024 * 1024)
    try:
        lines = data.decode('utf-8').splitlines()
    except UnicodeError:
        raise FunctionalCheckError('cli-history-file-invalid') from None
    headers = [i for i, line in enumerate(lines) if line.split() and line.split()[0] == 'Iter']
    if len(headers) != 1:
        raise FunctionalCheckError('cli-history-result-invalid')
    # All five supported source families use this steady history layout. Two
    # residual headings contain spaces; normalize those before checking row width.
    position = headers[0]
    header = re.sub(r'L2\s+Residual', 'L2_Residual', lines[position])
    header = re.sub(r'Max\s+Residual', 'Max_Residual', header).split()
    if tuple(header) != CLI_HISTORY_FIELDS:
        raise FunctionalCheckError('cli-history-result-invalid')
    rows = [line.split() for line in lines[position + 1:] if line.strip()]
    if not rows or any(len(row) != len(header) for row in rows):
        raise FunctionalCheckError('cli-history-result-invalid')
    try:
        values = [[float(value) for value in row] for row in rows]
    except ValueError:
        raise FunctionalCheckError('cli-history-result-invalid') from None
    # These two source-defined diagnostics are log10(residual): an exact zero
    # residual can legitimately be -Inf. No physical coefficient, lift, iteration
    # or elapsed-time value may be nonfinite, and NaN/+Inf residuals still fail.
    residuals = {header.index('L2_Residual'), header.index('Max_Residual')}
    if not all(math.isfinite(value) or (i in residuals and value == -math.inf)
               for row in values for i, value in enumerate(row)):
        raise FunctionalCheckError('cli-history-nonfinite')
    if abs(values[-1][6]) <= 1e-6:
        raise FunctionalCheckError('cli-history-lift-zero')
    return dict(lift_field='CLtot', samples=len(values), finite_lift=True,
                finite_physical_values=True, residual_semantics_verified=True,
                final_lift_nonzero=True, history_fresh=True)


def validate_functional_summary(summary):
    """Assembly must reject old, absent or incomplete functional evidence."""
    try:
        stl, comp, solver = summary['stl'], summary['compgeom'], summary['vspaero_api']
        cli = summary['vspaero_cli']
        valid = (type(summary['schema']) is int and summary['schema'] == 1
                 and summary['script_origin'] == 'pinned workflow tooling'
                 and summary['names_preserved'] is True and type(summary['api_errors']) is int
                 and summary['api_errors'] == 0 and stl['unicode_filename'] is True
                 and stl['format'] in ('ascii', 'binary') and type(stl['triangles']) is int
                 and stl['triangles'] > 0 and stl['finite_coordinates'] is True
                 and stl['nondegenerate_geometry'] is True and type(comp['regions']) is int
                 and comp['regions'] == 2 and comp['finite_positive_areas'] is True
                 and solver['lift_field'] in ('CLtot', 'CL') and type(solver['samples']) is int
                 and solver['samples'] > 0 and solver['finite_lift'] is True
                 and solver['final_lift_nonzero'] is True and type(cli['exit_code']) is int
                 and cli['exit_code'] == 0 and cli['lift_field'] == 'CLtot'
                 and type(cli['samples']) is int and cli['samples'] > 0
                 and cli['finite_lift'] is True and cli['finite_physical_values'] is True
                 and cli['residual_semantics_verified'] is True
                 and cli['final_lift_nonzero'] is True and cli['history_fresh'] is True)
    except (KeyError, TypeError):
        valid = False
    if not valid:
        raise ValueError('Required native export/analysis evidence is missing or invalid')
