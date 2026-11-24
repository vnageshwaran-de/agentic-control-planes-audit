#!/usr/bin/env python3
"""Step 3 (run after 01 and 03). Compute inter-rater reliability and build the
reliability workbook.

Reads B1_merged_grid.csv (from 01) and B1_FINAL_grid.csv (from 03) and writes
B1_audit_reliability.xlsx next to this script, with a Reliability sheet
(per-dimension and pooled weighted kappa_w, Gwet's AC2, cluster-bootstrap 95%
CIs), the raw R1'/R2' grid, and the reconciled FINAL grid. kappa_w is
cross-checked against scikit-learn when it is installed. Paths are relative to
this script.  Requires: openpyxl, numpy (scikit-learn optional).
"""
import csv, os
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
HERE = os.path.dirname(os.path.abspath(__file__))
np.random.seed(42)
dims = ['D1','D2','D3','D4','D5','D6']
dimname = {'D1':'D1 Capability description','D2':'D2 Authentication',
           'D3':'D3 Side-effect declaration','D4':'D4 Allow-list & sandboxing',
           'D5':'D5 Tracing','D6':'D6 Versioning & supply chain'}
rows = list(csv.DictReader(open(os.path.join(HERE, 'B1_merged_grid.csv'))))
G = {r['unit']: r for r in rows}; order = [r['unit'] for r in rows]
EXCL = {'C03','C11','C04'}
units = [u for u in order if u not in EXCL]
def val(u, d, rt):
    v = str(G[u][f'{d}_{rt}']).strip()
    return 'NA' if (v.upper()=='NA' or v in ('','None','UNSCOREABLE')) else int(float(v))
def wkappa(pairs, cats, quad=True):
    K = len(cats); idx = {c:i for i,c in enumerate(cats)}; O = np.zeros((K,K))
    for a,b in pairs: O[idx[a], idx[b]] += 1
    N = O.sum()
    if N == 0: return None
    W = np.array([[1-((i-j)**2)/((K-1)**2) for j in range(K)] for i in range(K)]) if quad else np.eye(K)
    r, c = O.sum(1), O.sum(0); E = np.outer(r,c)/N
    po, pe = (W*O).sum()/N, (W*E).sum()/N
    return (po-pe)/(1-pe) if (1-pe) != 0 else None
def ac2(pairs, cats, quad=True):
    K = len(cats); idx = {c:i for i,c in enumerate(cats)}; O = np.zeros((K,K))
    for a,b in pairs: O[idx[a], idx[b]] += 1
    N = O.sum()
    if N == 0: return None
    W = np.array([[1-((i-j)**2)/((K-1)**2) for j in range(K)] for i in range(K)]) if quad else np.eye(K)
    P = O/N; pa = (W*P).sum(); pi = (P.sum(1)+P.sum(0))/2; Tw = W.sum()
    pe = (Tw/(K*(K-1)))*np.sum(pi*(1-pi))
    return (pa-pe)/(1-pe) if (1-pe) != 0 else None
def numpairs(dl):
    return [(val(u,d,'R1'), val(u,d,'R2')) for u in units for d in dl
            if val(u,d,'R1') != 'NA' and val(u,d,'R2') != 'NA']
def boot(dl, fn, reps=3000):
    es = []
    for _ in range(reps):
        s = np.random.choice(units, len(units), replace=True)
        pr = [(val(u,d,'R1'), val(u,d,'R2')) for u in s for d in dl
              if val(u,d,'R1') != 'NA' and val(u,d,'R2') != 'NA']
        e = fn(pr, [0,1,2])
        if e is not None: es.append(e)
    return (np.percentile(es,2.5), np.percentile(es,97.5)) if es else (None, None)
def interp(k):
    return ('almost perfect' if k>=.81 else 'substantial' if k>=.61 else 'moderate'
            if k>=.41 else 'fair' if k>=.21 else 'slight' if k>=0 else 'poor')
try:
    from sklearn.metrics import cohen_kappa_score
except Exception:
    cohen_kappa_score = None

tab = []
for d in dims:
    pr = numpairs([d]); kw = wkappa(pr,[0,1,2]); a2 = ac2(pr,[0,1,2])
    pa = sum(1 for x,y in pr if x==y)/len(pr) if pr else None
    tab.append((dimname[d], len(pr), 21-len(pr), pa, kw, boot([d],wkappa), a2, boot([d],ac2), interp(kw)))
prall = numpairs(dims); kwall = wkappa(prall,[0,1,2]); a2all = ac2(prall,[0,1,2])
paall = sum(1 for x,y in prall if x==y)/len(prall)
ciw, cia = boot(dims,wkappa), boot(dims,ac2)
print(f'Reliability set: {len(units)} scoreable units')
print(f'Pooled: %agree={paall:.2f}  kappa_w={kwall:.3f} [{ciw[0]:.2f},{ciw[1]:.2f}]  AC2={a2all:.3f} [{cia[0]:.2f},{cia[1]:.2f}]')
if cohen_kappa_score:
    aa=[a for a,b in prall]; bb=[b for a,b in prall]
    print(f'scikit-learn cross-check kappa_w = {cohen_kappa_score(aa,bb,weights="quadratic",labels=[0,1,2]):.3f}')

# ---- workbook ----
ARIAL=Font(name='Arial',size=10); BOLD=Font(name='Arial',size=10,bold=True)
WB=Font(name='Arial',size=10,bold=True,color='FFFFFF'); HF=PatternFill('solid',fgColor='2F4F4F')
TOT=PatternFill('solid',fgColor='E2EFDA'); thin=Side(style='thin',color='BFBFBF')
BD=Border(left=thin,right=thin,top=thin,bottom=thin); ctr=Alignment(horizontal='center')
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Reliability'; ws.sheet_view.showGridLines=False
ws['A1']='B1 MCP security-posture audit - inter-rater reliability (blind re-run, rubric v2.0)'; ws['A1'].font=BOLD
H=['Dimension','n numeric pairs','n NA-excluded','% exact agree','weighted kappa_w','kappa_w 95% CI','Gwet AC2','AC2 95% CI','interpretation']
for j,h in enumerate(H,1):
    c=ws.cell(3,j,h); c.font=WB; c.fill=HF; c.border=BD; c.alignment=Alignment(wrap_text=True,horizontal='center',vertical='center')
r=4
for name,n,nna,pa,kw,ciwd,a2,ciad,itp in tab:
    for j,v in enumerate([name,n,nna,f'{pa*100:.0f}%',round(kw,3),f'[{ciwd[0]:.2f}, {ciwd[1]:.2f}]',round(a2,3),f'[{ciad[0]:.2f}, {ciad[1]:.2f}]',itp],1):
        c=ws.cell(r,j,v); c.font=ARIAL; c.border=BD; c.alignment=ctr if j>1 else Alignment(vertical='center')
    r+=1
for j,v in enumerate(['OVERALL (pooled)',len(prall),126-len(prall),f'{paall*100:.0f}%',round(kwall,3),f'[{ciw[0]:.2f}, {ciw[1]:.2f}]',round(a2all,3),f'[{cia[0]:.2f}, {cia[1]:.2f}]',interp(kwall)],1):
    c=ws.cell(r,j,v); c.font=BOLD; c.fill=TOT; c.border=BD; c.alignment=ctr if j>1 else Alignment(vertical='center')
for j,w in enumerate([30,13,13,12,13,16,10,16,15],1): ws.column_dimensions[get_column_letter(j)].width=w
# raw grid
rg=wb.create_sheet('Raw_grid_R1_R2')
hdr=['unit']+[f'{d} R1' for d in dims]+[f'{d} R2' for d in dims]
for j,h in enumerate(hdr,1): c=rg.cell(1,j,h); c.font=WB; c.fill=HF
for i,u in enumerate(order,2):
    rg.cell(i,1,u)
    for k,d in enumerate(dims):
        rg.cell(i,2+k,G[u][f'{d}_R1']); rg.cell(i,8+k,G[u][f'{d}_R2'])
# FINAL grid (optional; produced by 03)
fp=os.path.join(HERE,'B1_FINAL_grid.csv')
if os.path.exists(fp):
    fg=wb.create_sheet('FINAL_grid'); frows=list(csv.DictReader(open(fp)))
    for j,h in enumerate(['unit']+dims,1): c=fg.cell(1,j,h); c.font=WB; c.fill=HF
    for i,row in enumerate(frows,2):
        fg.cell(i,1,row['unit'])
        for k,d in enumerate(dims): fg.cell(i,2+k,row[d])
out=os.path.join(HERE,'B1_audit_reliability.xlsx'); wb.save(out); print('wrote', out)
