"""Validate the unrefined POD's actual dedicated UI VSPGEOM output."""
from math import isfinite
from pathlib import Path
import sys

mesh,key=map(Path,sys.argv[1:3])
assert mesh.parent == key.parent and mesh.stem == key.stem
lines=mesh.read_text().splitlines()
assert lines[0]=='# vspgeom v3', lines[:4]
assert int(lines[1])==1, 'unrefined single-POD mesh should declare one level'
points,faces,wakes=map(int,lines[2].split())
assert points>=3 and faces>0 and wakes==0,(points,faces,wakes)
assert '# FACE ERROR' not in '\n'.join(lines)
for row in lines[3:3+points]:
    coords=list(map(float,row.split()))
    assert len(coords)==3 and all(isfinite(v) for v in coords),coords
start=3+points
assert int(lines[start])==faces
face_rows=lines[start+1:start+1+faces]
assert len(face_rows)==faces
assert start+1+faces < len(lines), 'VSPGEOM trailing part/parent sections are absent'
largest=0
for row in face_rows:
    arity,*idx=map(int,row.split())
    assert arity>=3 and len(idx)==arity, row
    assert len(set(idx))==arity and all(1<=j<=points for j in idx), row
    largest=max(largest,arity)

tag=key.read_text().splitlines()
assert tag[0]=='# VSPGEOM v3 Tag Key File'
assert Path(tag[1]).name==mesh.name and int(tag[2])>0
assert any('SyntheticDegenMeshPod' in line for line in tag[3:])
print(f'PASS dedicated original GUI VSPGEOM: {points} finite points, {faces} valid faces (max {largest} nodes), POD has {wakes} wakes, matching source POD tag key')
