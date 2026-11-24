#!/usr/bin/env python3
"""Step 2. Build the reconciled FINAL posture grid.

Reads B1_merged_grid.csv (from 01) and the third-rater adjudication
(adjudication_R3_FINAL.xlsx); agreement cells keep the agreed score and
disagreements take R3's FINAL. Excludes C04 and the all-NA suite units
(C03, C11). Writes B1_FINAL_grid.csv. Paths are relative to this script.
"""
import openpyxl, csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
dims = ['D1','D2','D3','D4','D5','D6']
rows = list(csv.DictReader(open(os.path.join(HERE, 'B1_merged_grid.csv'))))
G = {r['unit']: r for r in rows}; order = [r['unit'] for r in rows]
def rawval(u, d, rt):
    v = str(G[u][f'{d}_{rt}']).strip()
    return 'NA' if (v.upper()=='NA' or v in ('','None','UNSCOREABLE')) else int(float(v))
wa = openpyxl.load_workbook(os.path.join(HERE, 'adjudication_R3_FINAL.xlsx'), data_only=True)
ws = wa['Adjudication']
dmap = {'D1 Capability description':'D1','D2 Authentication':'D2',
        'D3 Side-effect declaration':'D3','D4 Allow-list & sandboxing':'D4',
        'D5 Tracing':'D5','D6 Versioning & supply chain':'D6'}
fin = {}
for r in range(2, ws.max_row + 1):
    unit, dl, fv = ws.cell(r,3).value, ws.cell(r,5).value, ws.cell(r,14).value
    if dl in dmap:
        v = str(fv).strip(); fin[(unit, dmap[dl])] = 'NA' if v.upper()=='NA' else v
wa.close()
EXCL = {'C03','C11','C04'}
with open(os.path.join(HERE, 'B1_FINAL_grid.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['unit'] + dims)
    for u in order:
        if u in EXCL: continue
        out = [u]
        for d in dims:
            if (u, d) in fin: out.append(fin[(u, d)])
            else:
                a, b = rawval(u,d,'R1'), rawval(u,d,'R2')
                out.append(a if a == b else f'CONFLICT({a}/{b})')
        w.writerow(out)
print('wrote B1_FINAL_grid.csv')
