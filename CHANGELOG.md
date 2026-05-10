# Changelog

All notable changes to this project are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-05-10

### Added
- `run_kappa.py` — Cohen's weighted κ_w (quadratic weights on the {0, 1, 2} scale) computed between R1 (the human pilot scorer recorded in `audit_data.csv`) and R2 (the deterministic `extract_signals.py` script). Outputs a per-dimension κ table, the joint frequency matrix per dimension, and the overall pooled κ_w.
- `kappa_results.json` — full per-pair frequency matrices and per-dimension κ_w values, regenerable by `python3 run_kappa.py`.
- `methodology.md` §F1 — formal **inter-rater reliability protocol**: Cohen's weighted κ_w with quadratic weights, target κ ≥ 0.7 per Landis & Koch (1977), three-rater dispute resolution, and the published-in-advance commitment to release `audit_data_rater1.csv`, `audit_data_rater2.csv`, and the κ table at full IRR execution.
- `methodology.md` §F1.1 — **tool-vs-human comparison results**: per-dimension κ_w on the N=24 sample showing substantial agreement on D2 (0.801), D3 (0.727), D5 (0.732), and weaker agreement on D1, D4, D6 traceable to specific regex-faithfulness gaps.
- `methodology.md` §F1.1 — **v1.1 release plan**: the D6 README-text check is replaced by a query against the GitHub Releases API; D1 is redefined to measure capability-description *richness* (parameter constraints, risk-class annotations, signed metadata) rather than schema presence, deliberately preserving D1's discriminative power across the population of conforming MCP servers; D4 is designated a judgment dimension where script and human are expected to differ.

### Changed
- `README.md` — adds `run_kappa.py` and `kappa_results.json` to the contents list; bumps the cited release version to 1.1.0.
- `.gitignore` — explicit `!kappa_results.json` exception so the canonical script-vs-human comparison artifact is tracked alongside `audit_data.csv`.
- `CITATION.cff` — version 1.1.0 with 2026-05-10 release date.

### Notes
- The N=24 v1.0 pilot R1 scores in `audit_data.csv` remain the published baseline for the IEEE OJ-CS submission. The v1.1 rescore will be released as an erratum with both R1 and R2-script scores so reproducibility is auditable end-to-end.

## [1.0.0] — 2026-05-06

### Added
- Initial release accompanying the IEEE OJ-CS submission *Agentic AI Control Planes: A Systematic Survey of Protocols, Security, Cloud-Native LLMOps, and Governance* (Nageshwaran & Ezekiel, 2026).
- `extract_signals.py` — deterministic regex-only six-dimension scorer for public MCP server READMEs.
- `methodology.md` — rubric, sampling frame, threats to validity, and version policy.
- `audit_data.csv`, `aggregate_stats.md`, `sampling_log.md` — N=24 pilot data.
- `LICENSE` (MIT), `CITATION.cff`, `requirements.txt`, GitHub Actions CI smoke test.
