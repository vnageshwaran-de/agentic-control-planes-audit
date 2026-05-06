# Aggregate Statistics — MCP Server Security-Posture Audit

**Sample size:** N = 24 (7 official reference servers from `modelcontextprotocol/servers` + 17 third-party community/vendor servers).
**Audit date:** 2026-05-06.
**Excluded:** AgentDeskAI/browser-tools-mcp (deprecated by author at audit time), Azure/azure-mcp (archived), and two repositories whose URLs returned 404 at audit time. The exclusion list is preserved in `sampling_log.md` for reproducibility.

## A. Total-Score Distribution (out of 12)

| Score | Servers | Cumulative |
|------:|--------:|-----------:|
| 2     | 4       | 4 (16.7 %) |
| 3     | 3       | 7 (29.2 %) |
| 4     | 3       | 10 (41.7 %) |
| 5     | 3       | 13 (54.2 %) |
| 6     | 2       | 15 (62.5 %) |
| 7     | 2       | 17 (70.8 %) |
| 8     | 3       | 20 (83.3 %) |
| 9     | 3       | 23 (95.8 %) |
| 10    | 1       | 24 (100 %)  |
| 11–12 | 0       | 24          |

**Median total score = 5.5 / 12.** **Mean = 5.42 / 12 ≈ 45 %.** No server in the sample achieves the upper quartile (≥10) other than `grafana/mcp-grafana`.

## B. Reference vs Community Comparison

| Group | N | Mean total (out of 12) | Median |
|---|---:|---:|---:|
| Reference (`modelcontextprotocol/servers`) | 7 | **3.00** | 3 |
| Third-party community / vendor | 17 | **6.47** | 7 |

The reference servers score lower than the community sample, consistent with their authors' explicit declaration that they are "educational examples, not production-ready solutions" (per `modelcontextprotocol/servers` README). The implication is that the *canonical reference design pattern* — what most new MCP server authors look at first — does not emphasize authentication, observability, or supply-chain hygiene.

## C. Per-Dimension Distribution

For each dimension (D1–D6), share of servers scoring 0 / 1 / 2 (column totals = N=24).

| Dim | Name | 0 | 1 | 2 | Mean (0–2) | §VI threats most exposed when score = 0 |
|----|------|--:|--:|--:|----------:|-----|
| D1 | Capability description integrity | 0 | 9 | 15 | **1.63** | T3, T7 |
| D2 | Authentication surface | 7 | 8 | 9 | 1.08 | T10, T11 |
| D3 | Side-effect declaration | 7 | 10 | 7 | 1.00 | T8, T9, T15 |
| D4 | Allow-list / sandboxing | 13 | 5 | 6 | 0.71 | T6, T15 |
| D5 | Audit / observability hooks | 22 | 0 | 2 | **0.17** | T16 |
| D6 | Versioning / supply-chain hygiene | 3 | 21 | 0 | 0.88 | T6 |

**Strongest dimension: D1.** 15 of 24 servers (62.5 %) ship a typed, machine-readable tool schema, reflecting the MCP standard's emphasis on the `inputSchema` field. Even the lowest scorers in D1 score 1 — no server in the sample omits a schema entirely.

**Universal gap: D5 audit/observability.** 22 of 24 servers (91.7 %) provide *no* structured trace or audit hook. The two exceptions are `grafana/mcp-grafana` (Tempo / OTel-compatible) and `awslabs/mcp` (CloudWatch/OTel surfaces). This corroborates §IX R13 (Agent observability standards) — the gap is real and observable in the public-server population, not just in conceptual analysis.

**Second-strongest gap: D6 signed supply chain.** *No* server achieves the full score (signed releases or SBOM/provenance). 21 of 24 ship tagged releases (a baseline of versioning hygiene), but none publish verified provenance artifacts that an MCP host could machine-check before installation. This corroborates §VI T6 (MCP server compromise) and §IX R1 (Secure MCP server discovery).

**Authentication surface (D2) is bimodal.** 7 of 24 (all reference servers) require *no authentication*, presumably because the stdio transport assumes the host process trusts the spawned server. The remaining 17 split roughly evenly between API-key (8) and OAuth-grade (9). The bimodal distribution mirrors the protocol's intentional auth-out-of-band design but exposes a weak-default risk for community servers that copy the reference pattern without adding auth.

## D. Common-Gap Clusters

Cross-tabulating dimensions, four common gap profiles emerge:

- **G1 — "Reference baseline":** D2=0, D3∈{0,1}, D4∈{0,2}, D5=0, D6=1. Score range 2–5. All 7 reference servers fit.
- **G2 — "Vendor minimum":** D1≥1, D2=1, D3=0, D4=0, D5=0, D6∈{0,1}. Score 3–4. Examples: cloudflare, heroku, brave-search.
- **G3 — "Production-aware":** D1=2, D2=2, D3≥1, D4≥1, D5=0, D6=1. Score 6–8. Examples: stripe, supabase, notion, apify, mongodb, snowflake.
- **G4 — "Observability-mature":** D1=2, D2≥1, D3=2, D4=2, D5=2, D6=1. Score 9–10. Examples: grafana, awslabs.

Group G3 dominates (8 servers) and represents the modal posture of vendor-published MCP servers as of audit date. The jump from G3 (8 / 12) to G4 (10+ / 12) is gated almost entirely on D5 (observability), which most organisations have not yet wired into their MCP layer.

## E. Comparison Framing vs MCPCORPUS

The audit's pilot (N=24) is a thin slice of the public-server population. The MCPCORPUS dataset (Lin et al., 2025 IEEE/ACM ASE — entry `linmcpcorpus2025ase` in this manuscript's bibliography) catalogues ~14,000 public MCP servers. A reasonable next step is to cross-reference this rubric against MCPCORPUS by automating the signal extraction (regex patterns from §D of `methodology.md`) over the 14K servers.

In the manuscript we frame the present audit as **methodological pilot + descriptive snapshot**, with the population-scale measurement explicitly flagged as future work in §IX (extension of R15 — MCP/A2A bench).

## F. Internal-Validity Notes

- **Single-rater coding.** All 24 servers were scored by the same rater; the per-server `notes` column in `audit_data.csv` records the specific signals observed so a second rater can re-score from the same data.
- **README-signal heuristic.** Scoring relied on README + repo-page signals (releases tab, archive status). Source-level inspection of every server was out of scope for the pilot. Servers may carry features (e.g., signed releases, OTel hooks) that the README does not advertise; if so this audit understates their score.
- **Snapshot bias.** Scores reflect repo state on 2026-05-06. MCP servers are evolving rapidly and some scores will improve within months.
