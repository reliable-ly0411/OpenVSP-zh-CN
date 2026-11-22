import argparse
import hashlib
from pathlib import Path
import sys

def expected(mode, fixture):
    role, case = mode.split('-', 1)
    assert role in ('original', 'candidate')
    assert case in ('both', 'csv-fails', 'matlab-fails')
    original = role == 'original'
    h = ("Computing degenerate geometry...\nDone!\n"
         "--------------------------------\n\nWriting output...\n\n"
         "Wrote 1 components and 1 blank geoms\nto the following files:\n\n" if original
         else "正在计算退化几何…\n计算完成！\n"
              "--------------------------------\n\n正在写出结果…\n\n"
              "退化几何导出：1 个组件和 1 个空白几何\n输出文件：\n\n")
    fail = "FAILED TO OPEN: " if original else "无法打开："
    for format_name, ext in (('csv','csv'), ('matlab','m')):
        path = fixture.with_name(f'{fixture.stem}_DegenGeom.{ext}')
        h += f"\t{fail if case == format_name + '-fails' else ''}{path}\n"
    return h.encode('utf-8')

def exports(root):
    checks = 0
    for case in ('both', 'csv-fails', 'matlab-fails'):
        for fmt, ext in (('csv','csv'),('matlab','m')):
            files = [root/f'{role}-{case}.{ext}' for role in ('original','candidate')]
            if case == fmt + '-fails':
                assert not any(p.exists() for p in files), files
                checks+=1
                print(f'PASS {case} {ext}: both fail to publish a file')
                continue
            src, dst = [p.read_bytes() for p in files]
            assert src == dst and src, files
            if ext == 'csv':
                assert b'# NUMBER OF COMPONENTS\n1\n' in src and b'BLANK_GEOMS,1' in src
                assert b'BODY,SyntheticDegenControl,' in src and b'SyntheticDegenMass' in src
            else:
                assert b'degenGeom = [];' in src and b'SyntheticDegenMass' in src
            checks+=1
            print(f'PASS {case} {ext}: byte parity sha256=' + hashlib.sha256(src).hexdigest())
    assert checks == 6
    print('All six export positive/negative comparisons passed; original and candidate GUI clipboard checks are separate.')

if len(sys.argv)==5 and sys.argv[1]=='--clipboard':
    _,_,mode,fixture,actual=sys.argv
    got=Path(actual).read_bytes()
    want=expected(mode,Path(fixture))
    if got!=want:
        raise SystemExit(f'{mode}: clipboard mismatch\nactual={got!r}\nexpected={want!r}')
elif len(sys.argv)==3 and sys.argv[1]=='--exports':
    exports(Path(sys.argv[2]))
elif __name__=='__main__':
    raise SystemExit("expected --clipboard MODE ABSOLUTE_FIXTURE ACTUAL or --exports DIR")
