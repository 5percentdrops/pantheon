#!/usr/bin/env python3
"""
Build data/software-house-agents.json by parsing every agent .md file in agents/.
Run from the repo root: python3 scripts/build_bundle.py
"""
import os, json, re, sys
from pathlib import Path

# Resolve paths relative to the script's parent directory (= repo root)
REPO = Path(__file__).resolve().parent.parent
SRC  = REPO / "agents"
OUT  = REPO / "data" / "software-house-agents.json"

DESK_ORDER = ["governance", "backend", "frontend", "mobile", "mobile-design", "devops", "pinescript", "qa", "data"]

def parse_agent(path: Path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"No frontmatter in {path}")
    fm_raw, body = m.group(1), m.group(2)

    # Simple YAML parse — we control the format, so we don't need PyYAML
    fm = {}
    current_list_key = None
    for line in fm_raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key:
            fm[current_list_key].append(line[4:].strip())
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            current_list_key = None
            if val == "":
                fm[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                fm[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
            else:
                fm[key] = val

    # Split body into Markdown sections
    sections = {}
    cur_section = None
    cur_buf = []
    for line in body.splitlines():
        if line.startswith("## "):
            if cur_section:
                sections[cur_section] = "\n".join(cur_buf).strip()
            cur_section = line[3:].strip()
            cur_buf = []
        else:
            cur_buf.append(line)
    if cur_section:
        sections[cur_section] = "\n".join(cur_buf).strip()

    return {
        "id": fm["id"],
        "name": fm["name"],
        "person_name": fm.get("person_name", ""),
        "desk": fm["desk"],
        "runtime": fm["runtime"],
        "model": fm["model"],
        "reports_to": fm.get("reports_to", ""),
        "supervises": fm.get("supervises", []),
        "consumes_from": fm.get("consumes_from", []),
        "produces_for": fm.get("produces_for", []),
        "triggers": fm.get("triggers", []),
        "frequency": fm.get("frequency", ""),
        "priority": fm.get("priority", "3"),
        "tools": fm.get("tools", []),
        "storage": fm.get("storage", []),
        "personality": sections.get("Personality", ""),
        "role": sections.get("Role", ""),
        "inputs": sections.get("Inputs", ""),
        "outputs": sections.get("Outputs", ""),
        "skills": sections.get("Skills", ""),
        "rules_of_engagement": sections.get("Rules of Engagement", ""),
        "failure_modes": sections.get("Failure Modes", ""),
        "prompt_stub": sections.get("Prompt Stub", ""),
    }

def main():
    agents = []
    for desk in DESK_ORDER:
        d = SRC / desk
        if not d.exists():
            print(f"warn: desk directory missing: {d}", file=sys.stderr)
            continue
        for f in sorted(d.glob("*.md")):
            agents.append(parse_agent(f))

    # Count per desk for the summary
    desk_counts = {}
    desk_heads = {}
    for a in agents:
        desk_counts[a["desk"]] = desk_counts.get(a["desk"], 0) + 1
    # Head detection: prefer Project Manager for governance, "senior-*" for others;
    # fallback to the agent with the longest supervises list
    HEAD_PREFERENCES = {
        "governance": "project-manager",
        "backend": "senior-backend-dev",
        "frontend": "senior-frontend-dev",
        "mobile": "senior-mobile-dev",
        "mobile-design": "senior-mobile-designer",
        "devops": "senior-devops",
        "pinescript": "senior-pinescript-dev",
        "qa": "senior-qa",
        "data": "senior-data-analyst",
    }
    for desk in DESK_ORDER:
        desk_agents = [a for a in agents if a["desk"] == desk]
        if not desk_agents:
            continue
        # 1. Explicit preference
        pref = HEAD_PREFERENCES.get(desk)
        if pref and any(a["id"] == pref for a in desk_agents):
            desk_heads[desk] = pref
            continue
        # 2. Anyone named senior-*
        senior_prefix = [a for a in desk_agents if a["id"].startswith("senior-")]
        if senior_prefix:
            desk_heads[desk] = senior_prefix[0]["id"]
            continue
        # 3. Longest supervises list
        head = max(desk_agents, key=lambda a: len(a.get("supervises") or []))
        desk_heads[desk] = head["id"]

    bundle = {
        "version": 1,
        "house": "software-house",
        "description": "Multi-agent AI-native software development house. 20 agents across 9 desks covering backend, frontend, mobile, mobile design, DevOps, PineScript indicator development, QA, data, and backtesting. Brain/Hands pattern — Senior Advisors plan, Executors execute, Hermes self-learning loop compounds skill across projects.",
        "agent_count": len(agents),
        "desks": [
            {"id": d, "head": desk_heads.get(d, ""), "member_count": desk_counts.get(d, 0)}
            for d in DESK_ORDER if desk_counts.get(d, 0) > 0
        ],
        "agents": agents,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, indent=2))
    print(f"Wrote {len(agents)} agents to {OUT.relative_to(REPO)}")
    print(f"File size: {OUT.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()
