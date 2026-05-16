#!/usr/bin/env python3
"""
Validate the generated agentcompanies/v1 package at pantheon/.

Checks:
  1. Required files exist (COMPANY.md, README.md, LICENSE, .paperclip.yaml).
  2. COMPANY.md frontmatter has schema=agentcompanies/v1.
  3. Every agent directory has an AGENTS.md with required frontmatter.
  4. Exactly one root (reportsTo: null) — Arthur.
  5. All reportsTo slugs resolve to a real agent directory.
  6. Each agent's skills frontmatter references an existing SKILL.md.
  7. .paperclip.yaml uses only valid Paperclip adapter types.
  8. No leftover stale Arthur model strings in any generated file.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "pantheon"

if not PKG.exists():
    # The package is generated on demand by scripts/convert_to_agentcompanies_v1.py.
    # If it hasn't been generated yet, this check is a no-op rather than a failure.
    print("SKIP: pantheon/ not generated yet (run convert_to_agentcompanies_v1.py first).")
    sys.exit(0)

VALID_ADAPTERS = {
    "claude_local", "codex_local", "opencode_local", "pi_local",
    "cursor", "gemini_local", "openclaw_gateway",
    # V8.5: external adapter loaded via ~/.paperclip/adapter-plugins.json
    "hermes_local",
}

STALE_ARTHUR_PATTERNS = [
    re.compile(r"arthur\s+uses\s+sonnet", re.I),
    re.compile(r"arthur\s+uses\s+opus", re.I),
    re.compile(r"arthur\s+uses\s+deepseek", re.I),
    re.compile(r"arthur.*?:\s*ops\s*4", re.I),
    re.compile(r"arthur\s+model:\s*claude-opus", re.I),
    re.compile(r"arthur\s+model:\s*sonnet", re.I),
]

failures = []


def fail(msg):
    failures.append(msg)


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not m:
        return None, text
    front = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([\w]+)\s*:\s*(.*)$", line)
        if kv:
            front[kv.group(1)] = kv.group(2).strip()
    return front, text[m.end():]


# 1. Required files
for f in ("COMPANY.md", "README.md", "LICENSE", ".paperclip.yaml"):
    if not (PKG / f).exists():
        fail(f"missing required file: {f}")

# 2. COMPANY.md schema
company_front, _ = parse_frontmatter(PKG / "COMPANY.md")
if not company_front:
    fail("COMPANY.md missing frontmatter")
elif company_front.get("schema") != "agentcompanies/v1":
    fail(f"COMPANY.md schema must be 'agentcompanies/v1', got {company_front.get('schema')!r}")
elif company_front.get("slug") != "pantheon":
    fail(f"COMPANY.md slug must be 'pantheon', got {company_front.get('slug')!r}")

# 3 + 4 + 5. Agent dirs
agents_dir = PKG / "agents"
if not agents_dir.exists():
    fail("agents/ directory missing")
else:
    agent_slugs = set()
    roots = []
    reports_to_map = {}
    skills_referenced = {}
    for sub in sorted(agents_dir.iterdir()):
        if not sub.is_dir():
            continue
        agents_md = sub / "AGENTS.md"
        if not agents_md.exists():
            fail(f"missing {sub.name}/AGENTS.md")
            continue
        front, body = parse_frontmatter(agents_md)
        if not front:
            fail(f"{sub.name}/AGENTS.md missing frontmatter")
            continue
        slug = front.get("slug")
        if slug != sub.name:
            fail(f"{sub.name}/AGENTS.md slug {slug!r} != directory name")
        agent_slugs.add(sub.name)
        # reportsTo
        reports_to = front.get("reportsTo", "")
        reports_to_map[sub.name] = reports_to
        if reports_to in ("null", "~", ""):
            roots.append(sub.name)
        # name + title required
        for req in ("name", "title", "description"):
            if not front.get(req):
                fail(f"{sub.name}/AGENTS.md missing required field {req}")
        # skills (parse as list under 'skills:' line) — scan ONLY within frontmatter
        front_text_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", agents_md.read_text(encoding="utf-8"), flags=re.S)
        if front_text_match:
            front_text = front_text_match.group(1)
            m = re.search(r"^skills:\s*\n((?:\s*-\s*\S+\s*\n?)+)", front_text, flags=re.M)
            if m:
                sk_block = m.group(1)
                skill_refs = [r for r in re.findall(r"^\s*-\s*(\S+)", sk_block, flags=re.M) if r and r != "---"]
                skills_referenced[sub.name] = skill_refs

    # 4. Exactly one root
    if len(roots) == 0:
        fail("no agent has reportsTo: null (need one head, Arthur)")
    elif len(roots) > 1:
        fail(f"multiple agents with reportsTo: null: {roots}")
    elif roots[0] != "arthur":
        fail(f"root agent should be 'arthur', got {roots[0]!r}")

    # 5. All reportsTo resolve
    for slug, rt in reports_to_map.items():
        if rt in ("null", "~", ""):
            continue
        if rt not in agent_slugs:
            fail(f"{slug}/AGENTS.md reportsTo {rt!r} does not match any agent directory")

    # 6. Skill refs resolve
    skills_dir = PKG / "skills"
    if not skills_dir.exists():
        fail("skills/ directory missing")
    else:
        for slug, refs in skills_referenced.items():
            for ref in refs:
                if not (skills_dir / ref / "SKILL.md").exists():
                    fail(f"{slug}/AGENTS.md references skill {ref!r} but skills/{ref}/SKILL.md does not exist")

# 7. .paperclip.yaml adapter types
pc = (PKG / ".paperclip.yaml").read_text(encoding="utf-8")
for m in re.finditer(r"^\s*type:\s*(\S+)\s*$", pc, flags=re.M):
    t = m.group(1)
    if t not in VALID_ADAPTERS:
        fail(f".paperclip.yaml adapter type {t!r} not in valid set {sorted(VALID_ADAPTERS)}")

# 8. No stale Arthur model strings in generated files
for f in PKG.rglob("*.md"):
    text = f.read_text(encoding="utf-8")
    for pat in STALE_ARTHUR_PATTERNS:
        m = pat.search(text)
        if m:
            # Allow phrases in markdown body that explicitly mark deprecation
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line = text[line_start:line_end].lower()
            if "deprecated" in line or "older" in line:
                continue
            fail(f"{f.relative_to(PKG)}: stale Arthur model match {pat.pattern!r} in: {line.strip()[:120]!r}")
            break

if failures:
    print(f"FAIL: {len(failures)} issue(s) in pantheon/:")
    for m in failures:
        print(f"  {m}")
    sys.exit(1)

print(f"PASS: pantheon/ is a valid agentcompanies/v1 package "
      f"with {len(agent_slugs)} agents and proper reporting structure.")
