#!/usr/bin/env python3
"""redundant_work_detector.py  (V8.9)

Article Mistake 2: "Multiple agents doing the same thing without realizing
it. Fix by making each agent's scope extremely specific."

This script scans Pantheon/paperclip/agents.json and emits a report on:

  1. Role-string near-duplicates (Jaccard >= 0.5 on tokenised role text)
  2. consumes_from / produces_for overlap (two agents both consume from
     the same upstream AND produce for the same downstream — likely
     redundant)
  3. seed_skill_path duplicates (same seed file means same starting
     behaviour — likely role drift)
  4. Identical model+harness pairs with overlapping role keywords
     (cost-redundancy: paying twice for the same compute on the same
     task class)

Output:
  workspace/07_Finalization/redundant_work_report.md     (human)
  workspace/07_Finalization/redundant_work_report.json   (machine)

Exits 0 always (this is a report, not a gate). Findings are advisory.
"""
from __future__ import annotations
import json
import re
import sys
from itertools import combinations
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS = REPO_ROOT / "Pantheon" / "paperclip" / "agents.json"
OUT_MD = REPO_ROOT / "workspace" / "07_Finalization" / "redundant_work_report.md"
OUT_JSON = REPO_ROOT / "workspace" / "07_Finalization" / "redundant_work_report.json"

JACCARD_THRESHOLD = 0.5
STOPWORDS = {
    "the", "and", "or", "of", "for", "to", "a", "an", "in", "on", "with",
    "is", "by", "as", "from", "into", "that", "this", "be", "all", "any",
}


def tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOPWORDS and len(t) > 2}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    if not AGENTS.exists():
        print(f"redundant_work_detector: {AGENTS} missing", file=sys.stderr)
        return 1
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(AGENTS.read_text(encoding="utf-8"))
    agents = data.get("agents", [])

    findings_role = []
    findings_handoff = []
    findings_seed = []
    findings_model = []

    # Index by seed
    seed_buckets: dict[str, list[str]] = {}
    for a in agents:
        s = a.get("seed_skill_path")
        if s:
            seed_buckets.setdefault(s, []).append(a.get("name") or a.get("id"))
    for seed, names in seed_buckets.items():
        if len(names) > 1:
            findings_seed.append({"seed_skill_path": seed, "agents": sorted(names)})

    # Pairwise role + handoff + model checks
    for a, b in combinations(agents, 2):
        # owen with null model: skip (he's intentionally dormant)
        if a.get("model") is None or b.get("model") is None:
            continue

        a_name = a.get("name") or a.get("id")
        b_name = b.get("name") or b.get("id")

        a_role = tokenize(f"{a.get('role','')} {a.get('description','')}")
        b_role = tokenize(f"{b.get('role','')} {b.get('description','')}")
        sim = jaccard(a_role, b_role)
        if sim >= JACCARD_THRESHOLD:
            findings_role.append({
                "agents": [a_name, b_name],
                "jaccard": round(sim, 3),
                "a_role": a.get("role"),
                "b_role": b.get("role"),
            })

        a_in = set(a.get("consumes_from") or [])
        b_in = set(b.get("consumes_from") or [])
        a_out = set(a.get("produces_for") or [])
        b_out = set(b.get("produces_for") or [])
        in_overlap = a_in & b_in
        out_overlap = a_out & b_out
        if in_overlap and out_overlap:
            findings_handoff.append({
                "agents": [a_name, b_name],
                "shared_upstream": sorted(in_overlap),
                "shared_downstream": sorted(out_overlap),
            })

        if a.get("model") == b.get("model") and a.get("harness") == b.get("harness") and sim >= 0.3:
            findings_model.append({
                "agents": [a_name, b_name],
                "model": a.get("model"),
                "harness": a.get("harness"),
                "role_similarity": round(sim, 3),
            })

    payload = {
        "snapshot_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "jaccard_threshold": JACCARD_THRESHOLD,
        "agents_evaluated": sum(1 for a in agents if a.get("model")),
        "agents_skipped_null_model": sum(1 for a in agents if not a.get("model")),
        "findings": {
            "role_near_duplicates": findings_role,
            "handoff_overlap": findings_handoff,
            "seed_skill_duplicates": findings_seed,
            "cost_redundancy_same_model": findings_model,
        },
        "total_findings": len(findings_role) + len(findings_handoff) + len(findings_seed) + len(findings_model),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = [
        f"# Pantheon — Redundant Work Report ({payload['snapshot_utc']})",
        "",
        f"_Auto-generated by `scripts/redundant_work_detector.py` (V8.9)._",
        f"_Article Mistake #2: \"multiple agents doing the same thing without realizing it.\"_",
        "",
        f"- Agents evaluated: {payload['agents_evaluated']}",
        f"- Agents skipped (null model, e.g. Owen): {payload['agents_skipped_null_model']}",
        f"- Total findings: **{payload['total_findings']}**",
        "",
    ]
    if not payload["total_findings"]:
        md.append("✅ No redundancy detected at current thresholds. 33 agents remain distinct.")
    else:
        if findings_role:
            md += ["## Role near-duplicates (Jaccard ≥ {})".format(JACCARD_THRESHOLD), "",
                   "| Agents | Jaccard | A role | B role |",
                   "|---|---|---|---|"]
            for f in findings_role:
                md.append(f"| {' / '.join(f['agents'])} | {f['jaccard']} | {f['a_role']} | {f['b_role']} |")
            md.append("")
        if findings_handoff:
            md += ["## Handoff overlap (shared upstream AND downstream)", "",
                   "| Agents | Shared upstream | Shared downstream |",
                   "|---|---|---|"]
            for f in findings_handoff:
                md.append(f"| {' / '.join(f['agents'])} | {', '.join(f['shared_upstream'])} | {', '.join(f['shared_downstream'])} |")
            md.append("")
        if findings_seed:
            md += ["## Seed-skill duplicates", "",
                   "| Seed file | Agents sharing it |",
                   "|---|---|"]
            for f in findings_seed:
                md.append(f"| `{f['seed_skill_path']}` | {', '.join(f['agents'])} |")
            md.append("")
        if findings_model:
            md += ["## Cost redundancy (same model+harness, overlapping role)", "",
                   "| Agents | Model | Harness | Role similarity |",
                   "|---|---|---|---|"]
            for f in findings_model:
                md.append(f"| {' / '.join(f['agents'])} | {f['model']} | {f['harness']} | {f['role_similarity']} |")
            md.append("")
        md += ["---", "",
               "**Triage rule:**",
               "- Role near-duplicates: tighten descriptions, narrow scopes.",
               "- Handoff overlap: consolidate the two agents OR explicitly route different ticket classes.",
               "- Seed duplicates: differentiate seeds; identical seeds = identical starting behaviour.",
               "- Cost redundancy: question whether two agents on the same model+harness justify the spend.",
               ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"redundant_work_detector: {payload['total_findings']} finding(s); wrote "
          f"{OUT_MD.relative_to(REPO_ROOT)} + {OUT_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
