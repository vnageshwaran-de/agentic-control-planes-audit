#!/usr/bin/env python3
"""
run_kappa.py — Compute Cohen's weighted κ between R1 (human pilot scorer)
and R2 (the deterministic extract_signals.py script) on the N=24 sample
recorded in audit_data.csv. Output a per-dimension κ table and the joint
agreement matrix.

This is the script-vs-human comparison documented in methodology.md §F1.1.
It is *not* a substitute for an independent second human rater, but it
quantifies the agreement between the published rubric (as the script
implements it) and the human R1 scoring.

Usage:
    python3 run_kappa.py
"""
from __future__ import annotations
import csv
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Reuse the scoring function from the kit.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from extract_signals import score_repo_text   # noqa: E402

DIMS = ["D1", "D2", "D3", "D4", "D5", "D6"]
DIM_FULL_NAMES = {
    "D1": "Capability description integrity",
    "D2": "Authentication surface",
    "D3": "Side-effect declaration",
    "D4": "Allow-list / sandboxing posture",
    "D5": "Audit / observability hooks",
    "D6": "Versioning / supply-chain hygiene",
}

# Map our R1 column names (in audit_data.csv) to the dimension keys.
R1_COL = {
    "D1": "D1_schema",
    "D2": "D2_auth",
    "D3": "D3_sideeffect",
    "D4": "D4_allowlist",
    "D5": "D5_audit",
    "D6": "D6_versioning",
}


def fetch_readme(repo: str) -> str:
    """Fetch README.md from a github.com/<owner>/<repo> URL.

    Tries /blob/main, /blob/master, then case variants. Returns "" on failure.
    The script-as-R2 scoring then runs on whatever text is fetched (or the empty
    string, which scores 0 across the board — a defensible "no signal" floor).
    """
    if repo.startswith("modelcontextprotocol/servers/"):
        # Reference servers are subdirectories of one repo
        sub = repo.split("modelcontextprotocol/servers/")[1]
        candidates = [
            f"https://raw.githubusercontent.com/modelcontextprotocol/servers/main/{sub}/README.md",
        ]
    else:
        # Generic owner/repo path
        candidates = [
            f"https://raw.githubusercontent.com/{repo}/main/README.md",
            f"https://raw.githubusercontent.com/{repo}/master/README.md",
            f"https://raw.githubusercontent.com/{repo}/main/readme.md",
        ]
    for url in candidates:
        try:
            req = Request(url, headers={"User-Agent": "agentic-control-planes-audit/kappa"})
            with urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    return resp.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError):
            continue
    return ""


def load_r1(path: str = None) -> list[dict]:
    """Load R1 (human) scores from audit_data.csv."""
    if path is None:
        path = os.path.join(HERE, "audit_data.csv")
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cohens_weighted_kappa(pairs: list[tuple[int, int]]) -> dict:
    """Cohen's weighted κ with quadratic weights over the {0,1,2} scale.

    pairs is a list of (rater1_score, rater2_score) tuples for one dimension.
    """
    n = len(pairs)
    if n == 0:
        return {"kappa_w": float("nan"), "n": 0, "po": float("nan"), "pe": float("nan"),
                "agreement": float("nan")}
    # Joint frequency matrix o_ij over {0,1,2}^2
    o = [[0]*3 for _ in range(3)]
    for r1, r2 in pairs:
        o[r1][r2] += 1
    o_norm = [[o[i][j] / n for j in range(3)] for i in range(3)]
    # Marginals
    p1 = [sum(o_norm[i][j] for j in range(3)) for i in range(3)]
    p2 = [sum(o_norm[i][j] for i in range(3)) for j in range(3)]
    # Quadratic weights w_ij = (i-j)^2; max weight = 4
    w = [[(i-j)**2 for j in range(3)] for i in range(3)]
    # Numerator/denominator
    num = sum(w[i][j] * o_norm[i][j] for i in range(3) for j in range(3))
    den = sum(w[i][j] * p1[i] * p2[j] for i in range(3) for j in range(3))
    if den == 0:
        # All marginal mass on one cell — perfect agreement (or undefined; we report 1.0 if also num==0)
        return {"kappa_w": 1.0 if num == 0 else float("nan"),
                "n": n,
                "po": sum(o_norm[i][i] for i in range(3)),
                "pe": float("nan"),
                "agreement": sum(o_norm[i][i] for i in range(3)),
                "matrix": o}
    kappa_w = 1 - num / den
    return {
        "kappa_w": round(kappa_w, 3),
        "n": n,
        "po": round(sum(o_norm[i][i] for i in range(3)), 3),
        "agreement_unweighted": round(sum(o_norm[i][i] for i in range(3)), 3),
        "matrix": o,
    }


def main() -> int:
    rows = load_r1()
    print(f"Loaded N={len(rows)} R1 scores from audit_data.csv")
    print()

    # Score each repo with the script (R2)
    r2_scores: list[dict] = []
    for row in rows:
        repo = row["repo"]
        readme = fetch_readme(repo)
        if not readme:
            print(f"  [{row['id']}] {repo}: README fetch FAILED — scoring as zero baseline", file=sys.stderr)
        rep = score_repo_text(repo, readme, snapshot="kappa-run")
        r2_scores.append({
            "id": row["id"],
            "repo": repo,
            "D1": rep.D1, "D2": rep.D2, "D3": rep.D3,
            "D4": rep.D4, "D5": rep.D5, "D6": rep.D6,
        })
        print(f"  [{row['id']:<3}] {repo[:50]:<50} R2 = {rep.D1}{rep.D2}{rep.D3}{rep.D4}{rep.D5}{rep.D6}  total={rep.total()}")

    # Compute κ_w per dimension
    print()
    print("=" * 78)
    print("Cohen's weighted κ_w per dimension (R1 = human pilot, R2 = extract_signals.py)")
    print("=" * 78)
    print(f"{'Dim':<4} {'Name':<40} {'n':>4} {'P_o':>6} {'κ_w':>6}")
    print("-" * 78)
    overall_pairs = []
    results = {}
    for dim in DIMS:
        pairs = []
        for r1_row, r2_row in zip(rows, r2_scores):
            r1_v = int(r1_row[R1_COL[dim]])
            r2_v = int(r2_row[dim])
            pairs.append((r1_v, r2_v))
            overall_pairs.append((r1_v, r2_v))
        res = cohens_weighted_kappa(pairs)
        results[dim] = res
        print(f"{dim:<4} {DIM_FULL_NAMES[dim]:<40} {res['n']:>4} {res['agreement_unweighted']:>6.3f} {res['kappa_w']:>6.3f}")
    overall = cohens_weighted_kappa(overall_pairs)
    print("-" * 78)
    print(f"{'ALL':<4} {'Pooled across all six dimensions':<40} {overall['n']:>4} {overall['agreement_unweighted']:>6.3f} {overall['kappa_w']:>6.3f}")
    print()

    # Save full results
    out = {
        "n_servers": len(rows),
        "per_dimension": {dim: {k: (v if k != 'matrix' else v) for k, v in results[dim].items()} for dim in DIMS},
        "overall_pooled": overall,
        "r2_scores": r2_scores,
    }
    out_path = os.path.join(HERE, "kappa_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Full results written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
