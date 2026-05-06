#!/usr/bin/env python3
"""
extract_signals.py — Automated signal extraction for the MCP-server security-
posture audit (companion to methodology.md and §VIII.E of the manuscript).

Input  : a GitHub repository URL (or a local path to a checked-out repo).
Output : a JSON record with deterministic 0/1/2 scores for each of the six
         rubric dimensions (D1..D6) plus the per-signal evidence used.

Usage  :
    python3 extract_signals.py --repo https://github.com/grafana/mcp-grafana
    python3 extract_signals.py --repo-dir ./checkouts/grafana_mcp_grafana
    python3 extract_signals.py --batch sampling_log.csv > audit_data_auto.csv

The script is intentionally regex-only (no LLM, no fuzzy matching) so two
independent raters running it on the same repo at the same commit produce
identical scores. The 1-vs-2 boundaries that involve documentation-quality
judgment fall through to the human-readable `evidence` field; the script
records the matched regex(es) and lets a second rater audit the call.

Requires : Python 3.8+, `requests` (only needed for --repo URL mode).
License  : MIT-style; reuse permitted.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
from dataclasses import dataclass, field, asdict
from typing import Optional

# -----------------------------------------------------------------------------
# Rubric — patterns are case-insensitive unless noted. Each dimension's regex
# set maps directly to the prose rule in methodology.md §D.
# -----------------------------------------------------------------------------

PATTERNS = {
    # D1 capability description integrity (T3, T7)
    "D1_typed_schema": r"input(_|-)?schema|inputSchema|JSON\s+schema|zod\b|pydantic|jsonschema|@tool\b|@mcp\.tool",
    "D1_signed_schema": r"signed\s+schema|signature.{0,30}schema|cosign|attestation",

    # D2 authentication surface (T10, T11)
    "D2_oauth": r"\bOAuth\b|OAuth\s*2(\.[01])?|OIDC|openid\s+connect",
    "D2_apikey": r"API[\s_-]?key|access[\s_-]?token|bearer\s+token|personal\s+access\s+token|service\s+account|service\s+principal",
    "D2_no_auth": r"no\s+authentication\s+required|anonymous(\s+by\s+default)?|stdio\s+transport",

    # D3 side-effect declaration (T8, T9, T15)
    "D3_readonly_flag": r"--read[-_]?only|--readOnly|--readonly|read[-_]?only\s+mode|RO_MODE",
    "D3_sideeffect_class": r"side[\s-]?effect|destructive|mutating|writeable|writes? to|deletes?",
    "D3_machine_class": r"risk[\s_-]?class|tool[\s_-]?class|capability[\s_-]?class|action[\s_-]?type",

    # D4 allow-list / sandboxing posture (T6, T15)
    "D4_allow_list": r"allow[-_]?list|--allowed[-_]?[a-z]+|--enabled[-_]?tools|--toolsets|--features",
    "D4_sandbox": r"sandbox(ing)?|isolat(e|ion)|container(ize|ization)|seccomp|firejail",
    "D4_egress": r"egress\s+(control|allow)|outbound\s+allow|--blocked[-_]?[a-z]+",

    # D5 audit / observability hooks (T16)
    "D5_otel": r"OpenTelemetry|OTel\b|distributed\s+trac(ing|e)|spans?\b",
    "D5_struct_log": r"structured\s+log|json\s+log|audit\s+log",
    "D5_cloudwatch": r"CloudWatch|App\s*Insights|Tempo\b|Jaeger|Zipkin",

    # D6 versioning / supply-chain hygiene (T6)
    "D6_release": r"github\.com/[^/]+/[^/]+/releases",  # link to releases tab
    "D6_sbom": r"SBOM|software\s+bill\s+of\s+materials|cyclonedx|spdx",
    "D6_signed_release": r"sigstore|cosign|provenance|in[-_]?toto|attestation",
}


@dataclass
class ScoreReport:
    repo: str
    commit_or_snapshot: str
    D1: int = 0
    D2: int = 0
    D3: int = 0
    D4: int = 0
    D5: int = 0
    D6: int = 0
    evidence: dict = field(default_factory=dict)

    def total(self) -> int:
        return self.D1 + self.D2 + self.D3 + self.D4 + self.D5 + self.D6


def _match(text: str, key: str) -> list[str]:
    """Return all unique matches of PATTERNS[key] in text (case-insensitive)."""
    return list({m.group(0) for m in re.finditer(PATTERNS[key], text, re.IGNORECASE)})


def score_repo_text(repo: str, readme: str, releases_html: str = "",
                    snapshot: str = "") -> ScoreReport:
    """Apply the rubric to text already fetched.

    Caller passes the README content and (optionally) the releases-page HTML.
    The function is pure — no I/O — so two raters running it on the same input
    get identical scores.
    """
    rep = ScoreReport(repo=repo, commit_or_snapshot=snapshot)

    # --- D1 -------------------------------------------------------------------
    typed = _match(readme, "D1_typed_schema")
    signed = _match(readme, "D1_signed_schema")
    if signed:
        rep.D1 = 2
    elif typed:
        rep.D1 = 1     # presence of schema language; rater confirms 1 vs 2
    else:
        rep.D1 = 0
    rep.evidence["D1"] = {"typed": typed, "signed": signed}

    # --- D2 -------------------------------------------------------------------
    oauth = _match(readme, "D2_oauth")
    apik  = _match(readme, "D2_apikey")
    none  = _match(readme, "D2_no_auth")
    if oauth and apik:
        rep.D2 = 2
    elif oauth or apik:
        rep.D2 = 1 if not oauth else 2
    elif none:
        rep.D2 = 0
    else:
        rep.D2 = 0
    rep.evidence["D2"] = {"oauth": oauth, "apikey": apik, "no_auth": none}

    # --- D3 -------------------------------------------------------------------
    machine = _match(readme, "D3_machine_class")
    readonly = _match(readme, "D3_readonly_flag")
    se_prose = _match(readme, "D3_sideeffect_class")
    if machine or readonly:
        rep.D3 = 2
    elif se_prose:
        rep.D3 = 1
    else:
        rep.D3 = 0
    rep.evidence["D3"] = {"machine": machine, "readonly_flag": readonly,
                           "sideeffect_prose": se_prose}

    # --- D4 -------------------------------------------------------------------
    allow = _match(readme, "D4_allow_list")
    sand  = _match(readme, "D4_sandbox")
    egr   = _match(readme, "D4_egress")
    if allow and (sand or egr):
        rep.D4 = 2
    elif allow or sand or egr:
        rep.D4 = 1
    else:
        rep.D4 = 0
    rep.evidence["D4"] = {"allow_list": allow, "sandbox": sand, "egress": egr}

    # --- D5 -------------------------------------------------------------------
    otel = _match(readme, "D5_otel")
    sl   = _match(readme, "D5_struct_log")
    cw   = _match(readme, "D5_cloudwatch")
    if otel or cw:
        rep.D5 = 2
    elif sl:
        rep.D5 = 1
    else:
        rep.D5 = 0
    rep.evidence["D5"] = {"otel": otel, "struct_log": sl, "vendor_obs": cw}

    # --- D6 -------------------------------------------------------------------
    rel    = _match(readme + releases_html, "D6_release")
    sbom   = _match(readme, "D6_sbom")
    signed_rel = _match(readme, "D6_signed_release")
    if sbom or signed_rel:
        rep.D6 = 2
    elif rel:
        rep.D6 = 1
    else:
        rep.D6 = 0
    rep.evidence["D6"] = {"releases": bool(rel), "sbom": sbom,
                           "signed_release": signed_rel}

    return rep


def fetch_readme(repo_url: str) -> tuple[str, str]:
    """Fetch README.md for a github.com/<owner>/<repo> URL on default branch.

    Returns (readme_text, snapshot_label) where snapshot_label is the resolved
    default-branch HEAD SHA so the audit is reproducible.
    """
    import requests  # local import keeps the script importable without it

    parts = urllib.parse.urlparse(repo_url).path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"Cannot parse owner/repo from {repo_url!r}")
    owner, repo = parts[0], parts[1]

    api = f"https://api.github.com/repos/{owner}/{repo}"
    meta = requests.get(api, timeout=15).json()
    default_branch = meta.get("default_branch", "main")
    sha_url = f"{api}/commits/{default_branch}"
    sha = requests.get(sha_url, timeout=15).json().get("sha", "")[:12]

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/README.md"
    r = requests.get(raw_url, timeout=15)
    if r.status_code != 200:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/readme.md"
        r = requests.get(raw_url, timeout=15)
    return r.text if r.status_code == 200 else "", sha


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--repo", help="GitHub repo URL")
    src.add_argument("--repo-dir", help="Local checked-out repo path")
    src.add_argument("--readme-file", help="Path to a README file")
    ap.add_argument("--snapshot", default="", help="Optional commit/date label")
    args = ap.parse_args()

    if args.repo:
        text, sha = fetch_readme(args.repo)
        snap = args.snapshot or sha
        rep = score_repo_text(args.repo, text, snapshot=snap)
    elif args.repo_dir:
        path = os.path.join(args.repo_dir, "README.md")
        if not os.path.exists(path):
            path = os.path.join(args.repo_dir, "readme.md")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        rep = score_repo_text(args.repo_dir, text, snapshot=args.snapshot)
    else:
        with open(args.readme_file, encoding="utf-8") as f:
            text = f.read()
        rep = score_repo_text(args.readme_file, text, snapshot=args.snapshot)

    out = asdict(rep)
    out["total"] = rep.total()
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
