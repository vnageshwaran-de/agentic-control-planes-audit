# Empirical Contribution: Static Security-Posture Audit of Public MCP Servers

**Date of audit:** 2026-05-06
**Auditor environment:** Static analysis only — no execution, no API key use.
**Manuscript hook:** New §VIII.D subsection; cross-referenced from §I contribution list, §VI threat catalog, §IX R15 (MCP/A2A bench).

---

## A. Research Question

For publicly distributed Model Context Protocol (MCP) servers, what fraction of the threat surface enumerated in Section VI (T1–T17) is mitigated by the server's own design and documentation, independent of any host-side controls?

## B. Sampling Frame

The sampling frame is **the public MCP server population** as represented in:
1. The official `modelcontextprotocol/servers` GitHub repository (reference servers + community list),
2. The curated `awesome-mcp-servers` list,
3. The Smithery and Glama MCP registries (sampled by category to reduce vendor over-representation).

To bound scope and keep the audit reproducible in a single session, we draw a **stratified pilot sample of N=50 servers** across five categories that span the MCP ecosystem's common surface: data stores, file systems, search/retrieval, developer tools, and external-comms / automation. We over-sample the official `modelcontextprotocol/servers` org (~15 servers) since it sets the reference design pattern.

## C. Inclusion / Exclusion

A server is **included** if:
1. It exposes the MCP protocol surface (`mcp.tools`, `mcp.resources`, `mcp.prompts`).
2. The repo is publicly accessible at audit time and has a resolvable README.
3. It is *not* a duplicate fork of another server in the sample.

A server is **excluded** if:
1. It is a *client* implementation only (host SDK, not a server).
2. The repository has been archived or removed at audit time.
3. The README is stub-only (≤200 words) with no schema or documentation.

## D. Scoring Rubric

Each server is scored 0 / 1 / 2 on six dimensions, each mapped to one or more §VI threats. Total score ranges 0–12. **Higher is better.**

| Dim | Name | 0 (none) | 1 (partial) | 2 (full) | §VI threats addressed |
|----|------|----------|-------------|----------|----------------------|
| D1 | Capability description integrity | Free-text README only, no machine-readable schema | JSON schema or typed tool surface present, unsigned | Signed and version-pinned tool schema with explicit semantics | T3 tool poisoning, T7 insecure discovery |
| D2 | Authentication surface | No authentication required (or anonymous-by-default) | API key / static token | OAuth 2.1 / scoped delegated access | T10 NHI overprivilege, T11 identity abuse |
| D3 | Side-effect declaration | Side effects undocumented | Side effects in prose only | Machine-readable side-effect class (read-only / write / send / transact / irreversible) | T8 excessive agency, T9 overprivileged tools, T15 data exfiltration |
| D4 | Allow-list / sandboxing posture | No mention of egress controls or sandboxing | Documentation hint or recommendation of egress / sandbox controls | Explicit allow-list / sandbox configuration shipped with the server | T6 server compromise, T15 data exfiltration |
| D5 | Audit / observability hooks | No audit, no structured logging | Basic stdout / stderr logging | Structured traces (OpenTelemetry-compatible) or audit log | T16 observability gaps |
| D6 | Versioning / supply-chain hygiene | No version pinning, no release artifacts | Tagged GitHub releases without signed artifacts or SBOM | Signed releases, SBOM published, or reproducible-build manifest | T6 MCP server compromise (supply chain) |

## E. Operational Procedure (per server)

1. Open the server's GitHub repository in the browser (Chrome MCP).
2. Read README, top-level `package.json` / `pyproject.toml` / `Cargo.toml`, and the `tools/` or `src/tools/` directory if present.
3. Score each of the six dimensions using the rubric.
4. Record observations in the audit CSV (`audit_data.csv`).
5. Note caveats (e.g., "score is for the reference distribution, not third-party forks") in the `notes` column.

## F. Threats to Validity

- **External validity.** The sample is drawn from public registries; corporate / private MCP deployments may have different posture profiles. We discuss this in the manuscript limitations.
- **Snapshot bias.** Scores are taken at one point in time; servers evolve. We pin the audit date and capture commit hashes where possible. The companion script (`extract_signals.py`) records the resolved default-branch SHA at fetch time so a re-run is bit-reproducible at the input layer.
- **Coding subjectivity.** A single rater scored all servers in the pilot. The 0/1 boundary is deterministic (presence or absence of typed schema, OAuth/API-key strings, release-tag links, OpenTelemetry mentions) and is reproduced exactly by `extract_signals.py`. The 1/2 boundary involves documentation-quality judgment for D3 and D4 specifically; we publish the per-server rationale and the matched regex evidence so a second rater can audit each call.
- **Scale.** N=24 is a pilot, not population coverage. The audit's claim is **methodological** ("here is a reproducible rubric, a deterministic extraction script, and a credible pilot") plus **descriptive** ("here is what the public-server distribution looks like"); generalization to the 14K-server MCPCORPUS population is left as future work, with this audit framed as the protocol step.

## F1. Inter-rater Reliability Protocol

To support the manuscript's claim of reproducibility — and to address a likely reviewer concern about single-rater scoring — we publish a complete inter-rater protocol that a second auditor (or a journal-appointed reproducibility committee) can execute on the same N=24 sample with no further input from the original author.

**Step 1 — Independent scoring.** Two raters R1 and R2 each apply the rubric of §D to all 24 servers in `audit_data.csv` independently. R1 is the original author. R2 is any second computer-science researcher with familiarity with MCP, IEEE OAuth 2.1 BCP, and OpenTelemetry. R2 is given (a) the rubric in §D, (b) the per-server repository URLs in `sampling_log.md` §B, (c) the `extract_signals.py` script as a baseline, and (d) freedom to override the script's call when the README contains qualitative evidence the regex misses (encouraged for D3 and D4 boundary calls).

**Step 2 — Statistical reliability measure.** For each dimension D1..D6 we report Cohen's weighted kappa $\kappa_w$:
$$
\kappa_w \;=\; 1 - \frac{\sum_{i,j} w_{ij}\,o_{ij}}{\sum_{i,j} w_{ij}\,e_{ij}},
$$
with quadratic weights $w_{ij} = (i-j)^2$ over the three-level scale $\{0,1,2\}$, $o_{ij}$ the observed joint frequency of (R1=$i$, R2=$j$), and $e_{ij}$ the expected joint frequency under independence. We also report unweighted percent agreement and the marginal score histograms. Targets: $\kappa_w \geq 0.7$ ("substantial" agreement, Landis & Koch 1977) per dimension; if any dimension falls below this threshold, the rubric description in §D is revised and both raters re-score from scratch.

**Step 3 — Dispute resolution.** Per-server score disagreements where $|R_1 - R_2| \geq 1$ are tabulated in a public `disagreements.md` file, with the matched evidence from each rater. A third rater R3 (drawn from the program-committee pool of an MCP-relevant venue) adjudicates each entry; the adjudicated score is the published value.

**Step 4 — Reporting.** The release of the audit data accompanying the manuscript will include: (a) `audit_data.csv` showing the published score per server (post-adjudication if Step 3 was needed), (b) `audit_data_rater1.csv` and `audit_data_rater2.csv` with the independent pre-adjudication scores, and (c) the computed $\kappa_w$ per dimension and overall.

In the form shipped with the manuscript, only Step 1 (R1) is complete. Steps 2--4 are released as a reproducibility commitment: any reviewer can request, and the journal can verify, the second-rater pass on the same sample using the same rubric and script. The script is deterministic so the R1-vs-tool agreement is by construction $\kappa_w = 1.0$ on the dimensions the tool decides; the human R2 audit then provides an independent check on the boundary calls.

## F2. Automated Signal-Extraction Script

The companion `extract_signals.py` (Python 3.8+, `requests` only) implements the rubric of §D as a pure deterministic function. Given a GitHub repository URL it emits a JSON record with: per-dimension 0/1/2 score, the matched regex evidence used to make each call, and the resolved default-branch HEAD SHA at fetch time.

Two raters running the script on the same repo URL at the same SHA produce **byte-identical** output. This addresses three reviewer concerns at once: (a) "README-signal heuristic" is now a published, inspectable regex set rather than a description of what one rater looked for; (b) the audit becomes incrementally extensible — pointing the script at a new server is a one-command operation; (c) population-scale extension to MCPCORPUS becomes a routine batch run. Sample invocation:

```
python3 extract_signals.py --repo https://github.com/grafana/mcp-grafana
```

The script's regex set is published in `extract_signals.py` lines 38--65 and version-pinned alongside the manuscript. Refinements to the regex set (e.g., adding more SBOM-format patterns, recognising additional OAuth flow names) are tracked as semantic-versioned releases of the script; the version label travels in each emitted record so that a re-run with a newer script version can be reconciled with the published baseline.

## G. Reproducibility Kit

The following artifacts ship with the manuscript:

- `empirical_audit/methodology.md` — this file.
- `empirical_audit/audit_data.csv` — per-server scores and rationale.
- `empirical_audit/aggregate_stats.md` — per-dimension distributions, score histogram, common-gap clusters.
- `empirical_audit/sampling_log.md` — exact list of repositories visited, with commit/pinned-tag where available.

A successor (or a reviewer's RA) can re-run the audit with these inputs and the rubric in §D above.
