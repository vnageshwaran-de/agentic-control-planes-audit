# Audit re-run v2.0 — pinned, blind-rated, adjudicated (Fix 3 / B1)

This folder contains the re-run of the MCP security-posture audit that backs Section VIII
of the manuscript. It supersedes the original single-rater exploratory audit
(`../audit_data.csv`, `../run_kappa.py`) for all reliability and posture claims.

## What the re-run did
- **Pinned** each of the 24 implementation units to an upstream commit SHA and **archived** the
  snapshots, so both raters scored the identical artifact (`units_pinned.csv`,
  `snapshots_and_instruments.zip`).
- **Revised the rubric to v2.0 before scoring** (`rubric_v2.0.md`): D1 measures capability-description
  *richness* (not schema presence), D5 narrowed to agent-execution tracing, D6 scored from pinned
  release/provenance evidence, and an architecture-based **NA** code added.
- **Froze the evidence extractor** before scoring (`extract_signals_FROZEN_724f970.py`, commit 724f970).
- **Two raters scored blind** (`audit_rescore_B1_R1prime.xlsx` + the R2′ set encoded in the
  disagreements file); a **third rater adjudicated** all 45 disagreements
  (`adjudication_R3_FINAL.xlsx`).

## Scope
24 units pinned; **21 scoreable** (two all-NA monorepo suites and one deprecated/remote-hosted,
unpinnable unit excluded). Reliability and posture are reported on the 21.

## Headline results (see `B1_audit_reliability.xlsx`)
- Pooled **κ_w = 0.68 [0.57, 0.77]**, **Gwet AC2 = 0.70 [0.60, 0.79]**, 68% exact agreement
  (quadratic weights; unit-level cluster bootstrap, 3000 resamples, seed 42).
- Per-dimension κ_w: D2 0.85, D5 0.85, D3 0.77, D4 0.68, D1 0.58, **D6 −0.09** (AC2 0.41).
  D6's near-chance κ is a snapshot-scoping artifact (monorepo-root supply-chain config sits outside
  the per-server subpath snapshots) resolved at adjudication from pinned-root evidence at SHA
  `c799c855`.
- Reconciled posture: D5 agent-execution tracing is the weakest-documented dimension (16/21 document
  none); D6 strongest after adjudication (13/21 at 2).

## D6 reference-unit evidence
The seven reference servers (R01-R07) are published together from one monorepo, so their
D6 (versioning/supply-chain) evidence lives at the repository ROOT, outside the per-server
subpath snapshots. `d6_reference_evidence/` captures that root release configuration at the
pinned SHA (`c799c855`: OIDC trusted publishing + build provenance, protected release
environment, SHA-pinned actions, SECURITY.md), so the seven D6 scores are reproducible
without visiting the live repository.

## Reproduce
```
python 01_reconstruct_merged_grid.py   # join R1'+R2' score sheets -> B1_merged_grid.csv
python 03_build_final_grid.py          # + R3 adjudication -> B1_FINAL_grid.csv (reconciled posture)
python 02_compute_reliability.py       # both grids -> B1_audit_reliability.xlsx (kappa_w, AC2, bootstrap CIs)
```
All scripts read and write files in this directory (paths are relative to the script); run them in the order shown.
Requires `openpyxl`, `numpy`, `scikit-learn` (κ_w is cross-checked against scikit-learn).

## Open item
Adjudication was performed against the quoted rater evidence; a confirmatory pass over the archived
snapshots (priority: C01 and C02 on D6, where the raters disputed artifact *presence*) is the
remaining verification step. See `R3_snapshot_verification_cover_note.md` in the project.
