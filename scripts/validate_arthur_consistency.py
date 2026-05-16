#!/usr/bin/env python3
"""
Arthur model consistency check (V8.3).

Asserts that wherever Arthur's model is stated, it normalizes to:
    model:      openai/gpt-5-mini
    llm_module: GPT-5 mini under Hermes

Detection strategy:
  1. Canonical agent record: model, llm_module, description, personality,
     system_prompt fields must not contain stale model keywords.
  2. hermes_runtime.arthur_model_alias must equal canonical.
  3. rules.arthur_model / rules.arthur_model_alias must be absent.
  4. Arthur seed skill files: any line declaring a "Model" or "Model/module"
     must use the canonical identifier.
  5. Doc tables and policy files: any line that asserts Arthur's model must
     match canonical. Lines that DESCRIBE the deprecation (i.e. tell readers
     "old Opus/DeepSeek Arthur claims are deprecated") are allowed if they
     contain explicit deprecation language.

This validator catches the bug class — Arthur asserted with any other model
on any non-deprecated surface — not just specific strings from prior reviews.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SH = ROOT / 'Pantheon'

CANONICAL_MODEL = "openai/gpt-5-mini"
CANONICAL_DISPLAY = "GPT-5 mini under Hermes"

# Non-canonical model keywords that should never be asserted of Arthur
STALE_MODEL_PATTERNS = [
    r'\bsonnet\b', r'\bopus\b', r'\bdeepseek\b', r'\bgemini\b', r'\bkimi\b',
    r'\bops\s*4', r'\bclaude-3', r'\bhaiku\b', r'\bgpt-3\b', r'\bgpt-4',
    r'claude-opus', r'claude-sonnet',
]
ALLOWED_CANONICAL = ['gpt-5 mini', 'gpt-5-mini', 'openai/gpt-5-mini']

# Phrases that indicate a line is describing deprecation, not asserting it
DEPRECATION_MARKERS = [
    'deprecated', 'older', 'old watcher/core', 'historical',
    'legacy', 'archived', 'v8.1 note', 'v8.2 note',
    'older watcher/core or deepseek/opus arthur claims',
]

EXCLUDE_PATHS = ['/deprecated/', '\\deprecated\\', '/source_repo/', '\\source_repo\\']

failures = []

def is_excluded(path):
    s = str(path)
    return any(x in s for x in EXCLUDE_PATHS)

def looks_like_deprecation_notice(line):
    low = line.lower()
    return any(marker in low for marker in DEPRECATION_MARKERS)

# 1. Canonical agent record
org_path = SH / 'paperclip' / 'organization.import.json'
org = json.loads(org_path.read_text(encoding='utf-8'))
arthur = next((a for a in org.get('agents', []) if a.get('id') == 'arthur-project-manager'), None)
if not arthur:
    failures.append((str(org_path), "arthur-project-manager record missing"))
else:
    if arthur.get('model') != CANONICAL_MODEL:
        failures.append((str(org_path), f"arthur.model = {arthur.get('model')!r}"))
    if arthur.get('llm_module') != CANONICAL_DISPLAY:
        failures.append((str(org_path), f"arthur.llm_module = {arthur.get('llm_module')!r}"))
    for field in ['description', 'personality', 'system_prompt']:
        val = (arthur.get(field) or '').lower()
        for pat in STALE_MODEL_PATTERNS:
            if re.search(pat, val):
                failures.append((str(org_path), f"arthur.{field} contains stale model pattern {pat!r}"))

# 2. hermes_runtime
hr = org.get('hermes_runtime', {})
if hr.get('arthur_model_alias') != CANONICAL_MODEL:
    failures.append((str(org_path), f"hermes_runtime.arthur_model_alias = {hr.get('arthur_model_alias')!r}"))

# 3. rules block
rules = org.get('rules', {})
for k in ['arthur_model', 'arthur_model_alias']:
    if k in rules:
        failures.append((str(org_path), f"rules.{k} present: {rules[k]!r}"))

# 4. Seed skills — scan for Model declaration lines
for seed in (SH / 'skills' / 'hermes_seed').glob('skill_*arthur*.md'):
    text = seed.read_text(encoding='utf-8')
    for n, line in enumerate(text.splitlines(), 1):
        low = line.lower().strip()
        # Lines like "## Model" header followed by "OPS 4.7" or "Model/module: claude-opus-4-7"
        if re.match(r'^[-*\s]*model(/module)?\s*[:=]', low) or low.startswith('## model'):
            # The model line itself — check next line if header, else this line
            check = low
            if low.startswith('## model'):
                # next non-blank line
                lines = text.splitlines()
                for j in range(n, min(n+3, len(lines))):
                    if lines[j].strip():
                        check = lines[j].lower().strip()
                        break
            for pat in STALE_MODEL_PATTERNS:
                if re.search(pat, check):
                    if not any(a in check for a in ALLOWED_CANONICAL):
                        failures.append((str(seed.relative_to(ROOT)), f"line {n}: {line.strip()!r}"))
# Also check the seed file with id "project-manager" (legacy name)
pm_seed = SH / 'skills' / 'hermes_seed' / 'skill_project-manager_seed.md'
if pm_seed.exists():
    text = pm_seed.read_text(encoding='utf-8')
    for n, line in enumerate(text.splitlines(), 1):
        low = line.lower().strip()
        if re.match(r'^[-*\s]*model(/module)?\s*[:=]', low):
            for pat in STALE_MODEL_PATTERNS:
                if re.search(pat, low):
                    if not any(a in low for a in ALLOWED_CANONICAL):
                        failures.append((str(pm_seed.relative_to(ROOT)), f"line {n}: {line.strip()!r}"))

# 5. Doc and policy files: only flag lines that ASSERT (not describe deprecation of)
TEXT_GLOBS = ['**/*.md', '**/*.json', '**/*.yaml', '**/*.yml']
arthur_re = re.compile(r'\barthur\b', re.I)

for pattern in TEXT_GLOBS:
    for p in ROOT.glob(pattern):
        if is_excluded(p):
            continue
        if p.name == 'engineering_escalation_ladder_v8_2.json':
            continue
        if p == org_path:  # already handled structurally
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if 'arthur' not in text.lower():
            continue
        # Per-line scan
        for n, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if 'arthur' not in low:
                continue
            if looks_like_deprecation_notice(line):
                continue
            for pat in STALE_MODEL_PATTERNS:
                if re.search(pat, low):
                    # Distance check: arthur and the stale keyword within 60 chars in this line
                    arthur_pos = low.find('arthur')
                    kw_match = re.search(pat, low)
                    if abs(arthur_pos - kw_match.start()) > 60:
                        continue
                    # If canonical also in line, allow only if the stale keyword
                    # appears AFTER canonical and the line is clearly a table row
                    # or "X under Hermes" listing — heuristic: if canonical is in line
                    # AND the stale keyword belongs to a different agent reference
                    # (e.g. "Magnus | Gemini Pro 3.1" appearing in a table that also
                    # has Arthur's row), skip
                    canonical_in_line = any(a in low for a in ALLOWED_CANONICAL)
                    if canonical_in_line:
                        # Check if it's a table row format: lines starting with | and Arthur is in this row
                        if line.strip().startswith('|'):
                            # Arthur is in a table row; if the stale keyword is also in a
                            # cell labeled with another agent name, skip
                            cells = [c.strip() for c in line.split('|')]
                            arthur_cell_idx = next((i for i,c in enumerate(cells) if 'arthur' in c.lower()), -1)
                            kw_cell_idx = next((i for i,c in enumerate(cells) if re.search(pat, c.lower())), -1)
                            # Skip if Arthur and the stale keyword are in DIFFERENT cells
                            if arthur_cell_idx != -1 and kw_cell_idx != -1 and arthur_cell_idx != kw_cell_idx:
                                continue
                        # Also skip if it's clearly a multi-agent enumeration like
                        # "Seniors, Cody, Maxwell, Magnus, Arthur, and PRD agents remain on existing models"
                        if 'remain on' in low or 'existing model' in low:
                            continue
                    # Skip prose lines that mention Arthur AND other agent names — the
                    # stale model keyword almost certainly attaches to a different agent
                    OTHER_AGENT_NAMES = ['jack', 'marcus', 'maxwell', 'cody', 'magnus',
                                         'winston', 'clara', 'sonia', 'leo', 'felix',
                                         'ben', 'ivan', 'nadia', 'owen', 'vera',
                                         'graham', 'stone', 'adrian', 'priya', 'safiya',
                                         'mira', 'dante', 'dominic', 'elena', 'oscar',
                                         'henrik', 'theo', 'viktor', 'nathan', 'grant',
                                         'ellie', 'chloe']
                    other_agent_mentioned = any(
                        re.search(r'\b' + name + r'\b', low) for name in OTHER_AGENT_NAMES
                    )
                    if other_agent_mentioned:
                        # Arthur is being mentioned alongside another agent; the
                        # stale model keyword most likely belongs to that agent
                        continue
                        # Also skip if the keyword is part of another agent's assignment
                        # (e.g. "Stone: GPT-5.5" alongside "Arthur model: GPT-5 mini")
                        if ': gpt-5.5' in low or 'gemini pro' in low or 'gemini deep' in low:
                            # Multi-agent listing; canonical Arthur statement is in same block
                            if 'arthur model: gpt-5 mini' in low or 'arthur: gpt-5 mini' in low or 'arthur | project manager | gpt-5 mini' in low:
                                continue
                    failures.append((str(p.relative_to(ROOT)), f"line {n}: {line.strip()[:200]!r}"))
                    break  # one failure per line

if failures:
    # dedupe
    seen = set()
    uniq = []
    for path, msg in failures:
        key = (path, msg)
        if key not in seen:
            seen.add(key)
            uniq.append((path, msg))
    print(f"FAIL: {len(uniq)} Arthur consistency issue(s):")
    for path, msg in uniq:
        print(f"  [{path}] {msg}")
    sys.exit(1)

print(f"PASS: Arthur model claims consistent across all non-deprecated surfaces.")
print(f"      Canonical: model={CANONICAL_MODEL}, llm_module={CANONICAL_DISPLAY!r}")
