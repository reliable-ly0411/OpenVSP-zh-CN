"""Strict adjunct only. Run after, not in place of, original package gates."""
import argparse
import hashlib
from pathlib import Path
import subprocess

OFFICIAL = 'ca4958f2cf98d5e787a2a3fa37efb497e4903902'
OFFICIAL_TREE = '104d45707ec5ffa55e0df544c70a4377bc64c3c5'
RC17 = '42ca95e36890a2f109783e0ef07af216bbd5f5eb'
RC17_TREE = 'aac3c47cb5be4793b2720c3e41a8bf383f6ff569'
MODELS = {
    'Community_Vans_RV-12.vsp3', 'NASA_N2A_Hybrid_Wing_Body.vsp3',
    'NASA_Six-Passenger_Tiltwing_UAM.vsp3', 'NASA_X-57_Maxwell_Simplified_CRM_v4.4.1.vsp3',
    'Uber_eCRM-002_Lift-Plus-Cruise.vsp3',
}
EXAMPLES = {f'examples/Complete_Aircraft/{p}' for p in MODELS} | {
    'examples/Complete_Aircraft/SOURCES_AND_LICENSES.md', 'examples/README_zh-CN.md',
}
CORE_DISPLAY = {'src/geom_core/CustomGeom.cpp', 'src/geom_core/CustomGeom.h'}
LOCK_DIRS = ('src/cfd_mesh/', 'src/geom_api/', 'src/geom_core/', 'src/util/',
             'src/vsp_graphic/', 'src/xmlvsp/', 'Libraries/')
FEA_PNG_STEMS = ('VSPCircXSec','VSPPipeXSec','VSPIXSec','VSPRectXSec','VSPBoxXSec')

def require(condition, detail):
    if not condition:
        raise SystemExit(detail)

def audit(args):
    def git(*cmd):
        return subprocess.check_output(['git', '-C', args.source, *cmd])
    def rev(expr):
        return git('rev-parse', '--verify', expr).strip().decode('ascii')
    for ref, tree in [(OFFICIAL, OFFICIAL_TREE),(RC17, RC17_TREE),(args.head, args.tree)]:
        require(rev(ref + '^{commit}') == ref and rev(ref + '^{tree}') == tree,
                'Wrong provenance ref or tree ' + ref)
    if not args.audit_only:
        require(rev('HEAD') == args.head, 'Source checkout does not match the reviewed head')
        git('merge-base','--is-ancestor',OFFICIAL,args.head)
        require(not git('status','--porcelain'), 'Source checkout is not clean')
    git('merge-base','--is-ancestor',RC17,args.head)
    snap = git('diff-tree','-r','--raw','--abbrev=40','--no-commit-id','--no-renames','-z',OFFICIAL,args.head)
    manifest = Path(args.manifest).read_bytes()
    require(hashlib.sha256(manifest).hexdigest() == args.manifest_sha,
            'Wrong reviewed manifest digest')
    require(snap == manifest, 'Candidate net diffs differ from reviewed scope manifest')
    raw = snap.rstrip(b'\0').split(b'\0')
    paths = {p.decode('utf8'): raw[2*i].split()[-1].decode('ascii') for i,p in enumerate(raw[1::2])}
    diff_example = {p:s for p,s in paths.items() if p.startswith('examples/')}
    require(diff_example=={p:'A' for p in EXAMPLES}, 'Unexpected stock example changes')
    for p in EXAMPLES:
        require(rev(args.head + ':' + p) == rev(RC17 + ':' + p), 'Approved example changed: ' + p)
    require({p for p in paths if p.startswith(LOCK_DIRS)}==CORE_DISPLAY, 'Unexpected core/library changes')
    # This audit does not certify what GUI differences do. The supplied exact
    # manifest is the reviewed change boundary, not an unrestricted directory allowlist.
    for p in ('src/gui_and_draw/PSliceScreen.h','src/gui_and_draw/ManageMeasureScreen.cpp',
              'src/test/CMakeLists.txt','src/vsp/apitest_main.cpp', 'Libraries/cmake/External_FLTK.cmake'):
        require(rev(args.head + ':' + p) == rev(OFFICIAL + ':' + p), 'Official blob changed: ' + p)
    screen = git('show', args.head + ':src/gui_and_draw/ScreenBase.cpp')
    for stem in FEA_PNG_STEMS:
        require(('"' + stem + '.png"').encode() in screen and
                ('"' + stem + '.PNG"').encode() not in screen, 'FEA asset lookup differs: ' + stem)
        p = 'examples/textures/' + stem + '.PNG'
        require(rev(args.head + ':' + p) == rev(OFFICIAL + ':' + p), 'FEA asset changed: ' + p)
    snap_src = git('show',args.head + ':src/gui_and_draw/ScreenBase.cpp')
    require(b'SnapshotTabCaption( c )' in snap_src and b'DumpFileName( name )' in snap_src
            and b'm_FileNames.Next' not in snap_src, 'Snapshot label/output paths not isolated')
    degen = git('show', args.head + ':src/gui_and_draw/DegenGeomScreen.cpp')
    require(b'->WriteDegenGeomFile();' in degen and b'FormatDegenGeomWriteStatus( report, paths )' in degen,
            'Degen writer must be official unmodified; translation may touch display only')
    print(f'Verified {args.head}, {len(paths)} pinned changed paths, official core, five reviewed models')
    
if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source', required=True)
    p.add_argument('--head', required=True)
    p.add_argument('--tree', required=True)
    p.add_argument('--manifest', required=True)
    p.add_argument('--manifest-sha', required=True)
    p.add_argument('--audit-only', action='store_true',
                   help='Allow isolated bare/tree audit; not permitted for CI')
    audit(p.parse_args())
