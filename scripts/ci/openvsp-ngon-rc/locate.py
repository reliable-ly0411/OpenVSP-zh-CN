"""Locate one positively identified, visible FLTK label from 2x OCR TSV."""
import csv
import re
import sys

with open(sys.argv[1], encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
def normalized(s):
    return re.sub(r'[^\w]|_', '', s).casefold()
target = normalized(sys.argv[2])
groups = {}
for row in rows:
    if row.get('level') == '5' and row.get('text', '').strip():
        key=tuple(row[k] for k in ('block_num','par_num','line_num'))
        groups.setdefault(key,[]).append(row)
matches=set()
for group in groups.values():
    for start in range(len(group)):
        for end in range(start+1,min(len(group),start+4)+1):
            span=group[start:end]
            if normalized(''.join(w['text'] for w in span))!=target:
                continue
            x=min(int(w['left']) for w in span)
            y=min(int(w['top']) for w in span)
            X=max(int(w['left'])+int(w['width']) for w in span)
            Y=max(int(w['top'])+int(w['height']) for w in span)
            matches.add(((x+X)//4,(y+Y)//4))
# The real Noble RC tab OCR may segment 其他 once as one word and
# again as two glyphs. One compact region in the exact tabs band is
# one label; all separated occurrences (and all other targets) fail.
if sys.argv[2] == "其他" and matches:
    xs, ys = zip(*matches)
    if (125 <= min(xs) <= max(xs) <= 155 and 32 <= min(ys) <= max(ys) <= 46
            and max(xs) - min(xs) <= 12 and max(ys) - min(ys) <= 4):
        matches = {((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2)}
if len(matches)!=1:
    raise SystemExit(f'Expected one visual label {sys.argv[2]!r}, found {sorted(matches)}')
print(*next(iter(matches)))
