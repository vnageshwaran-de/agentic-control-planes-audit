# MCP security-posture audit rubric — v2.0 (FROZEN before scoring)

Revised per referee Fix 3. Freeze this file with a git tag BEFORE any human scoring.
Companion deterministic script `extract_signals.py` FROZEN at commit 724f970 (2026-05-06),
run before human scoring (removes the script-vs-human circularity question).

Scale per dimension: 0 (none) · 1 (partial) · 2 (full) · NA (not applicable / host-provided).
Score strictly from the archived snapshot in `snapshots/<id>/` (pinned SHA in units_pinned.csv).
Record the exact evidence (file + line/quote) for every non-zero and every NA.

## D1 — Capability-description integrity  (threats T3 tool poisoning, T7 insecure discovery)
CHANGED v2.0: measures description *richness*, not mere schema presence.
- 0: tools listed with names only, or no machine-readable tool schema.
- 1: input schemas present but no parameter constraints, risk class, or behavioral hints.
- 2: schemas PLUS parameter constraints/validation AND risk-class or behavioral annotations
     (e.g. readOnlyHint/destructiveHint/idempotentHint/openWorldHint) documented.
- NA: capability description is supplied by the host/framework, not the server.

## D2 — Authentication surface  (T10 overprivileged accounts, T11 identity abuse)
- 0: no auth documented / implied open access.
- 1: auth mechanism named (API key/OAuth) but no scope/least-privilege guidance.
- 2: auth + documented scoping/least-privilege and token-handling guidance.
- NA: auth enforced entirely by the host runtime, not the server.

## D3 — Side-effect declaration  (T8 excessive agency, T9 overprivileged tools, T15 exfiltration)
- 0: no statement of which tools mutate state / are destructive.
- 1: some tools flagged (prose) but not systematically per tool.
- 2: per-tool side-effect/destructive declaration (machine-readable or exhaustive prose).
- NA: read-only server with no state-changing tools (document the basis).

## D4 — Allow-list & sandboxing posture  (T6 server compromise, T15 exfiltration)
- 0: no allow-list, path/root restriction, or sandbox guidance.
- 1: partial (e.g. path roots OR network egress controls, not both).
- 2: documented allow-listing AND execution/network sandboxing guidance.
- NA: no file/network/exec surface to constrain (document the basis).

## D5 — Agent-execution tracing  (T16 observability gaps)   *** NARROWED v2.0 ***
CHANGED v2.0: scores agent-execution *tracing* only — emitted spans/traces of tool
invocations — NOT any logging or observability mention.
- 0: no emitted trace/span of tool execution documented.
- 1: logging of invocations mentioned, but not structured/exportable traces.
- 2: structured execution traces/spans emitted and exportable
     (e.g. OpenTelemetry GenAI spans, documented span attributes).
- NA: tracing is the host/runtime's responsibility and the server documents that boundary.

## D6 — Versioning & supply-chain hygiene  (T6 supply chain)   *** CHANGED v2.0 ***
CHANGED v2.0: verified against the GitHub Releases API at the pinned SHA, not README prose.
- 0: no tagged releases / no versioning.
- 1: semantic-versioned tagged releases, but no signing/SBOM/provenance.
- 2: signed releases OR published SBOM/provenance (SLSA/attestation) at the pinned commit.
- NA: distributed only via a managed registry that signs on the server's behalf (document it).

## Scoring protocol (Fix 3)
1. Two raters (R1', R2') score ALL units independently, BLIND to each other, in the same week,
   from the archived snapshots only.
2. A third rater (R3') adjudicates every per-dimension disagreement.
3. Report per-dimension weighted kappa_w (quadratic) WITH bootstrap 95% CIs, PLUS Gwet's AC2
   (or Krippendorff's alpha) for marginal robustness. If a dimension still fails, say so in one line.
