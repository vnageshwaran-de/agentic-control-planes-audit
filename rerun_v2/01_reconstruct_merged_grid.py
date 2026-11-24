#!/usr/bin/env python3
"""Step 1. Build the merged R1'/R2' audit grid by joining the two blind score
sheets (audit_rescore_B1_R1prime.xlsx, audit_rescore_B1_R2prime.xlsx) on unit id.
Writes B1_merged_grid.csv next to this script. Paths are relative to this script.
"""
import openpyxl, csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
dims = ['D1','D2','D3','D4','D5','D6']
dcol = {'D1':7,'D2':9,'D3':11,'D4':13,'D5':15,'D6':17}  # 'Score' sheet columns
def norm(v):
    if v is None: return None
    s = str(v).strip()
    if s == '': return None
    if s.upper() in ('NA','UNSCOREABLE'): return s.upper() if s.upper()=='NA' else 'UNSCOREABLE'
    try: return int(float(s))
    except ValueError: return s
def load(fn):
    wb = openpyxl.load_workbook(os.path.join(HERE, fn), data_only=True); ws = wb['Score']
    g, order = {}, []
    for r in range(2, ws.max_row + 1):
        uid = ws.cell(r, 1).value
        if not uid: continue
        order.append(uid); g[uid] = {d: norm(ws.cell(r, dcol[d]).value) for d in dims}
    wb.close(); return g, order
R1, order = load('audit_rescore_B1_R1prime.xlsx')
R2, _     = load('audit_rescore_B1_R2prime.xlsx')
def cell(g, u, d):
    v = g.get(u, {}).get(d)
    return '' if v is None else v
with open(os.path.join(HERE, 'B1_merged_grid.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['unit'] + [f'{d}_R1' for d in dims] + [f'{d}_R2' for d in dims])
    for u in order:
        w.writerow([u] + [cell(R1,u,d) for d in dims] + [cell(R2,u,d) for d in dims])
print(f'wrote B1_merged_grid.csv ({len(order)} units) by joining R1prime + R2prime')
