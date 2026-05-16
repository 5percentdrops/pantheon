#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
required = [
 "WINSTON_KNOWLEDGE_ARCHITECTURE.md",
 "winston_knowledge_architecture_policy.md",
 "winston_archival_routes.json",
 "winston_artifact_archive.schema.json",
 "WINSTON_ARTIFACT_ARCHIVE.template.md",
 "WINSTON_ERROR_SOLUTION_LOG.template.md",
 "skill_winston-director-knowledge-architecture_seed.md",
 "winston_guidance.md",
 "universal_wiki_wrapper.sh",
 "write_wiki_doc.tool.yaml",
 "universal_wiki_wrapper.tool.yaml"
]
for fname in required:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")
for d in ["wiki/prds", "wiki/sdds", "wiki/tickets", "wiki/errors", "wiki/codebase"]:
    if not (ROOT / d).exists():
        errors.append(f"missing directory: {d}")
agents = []
for p in ROOT.rglob("organization.import.json"):
    try:
        agents += json.loads(p.read_text(encoding="utf-8")).get("agents", [])
    except Exception:
        pass
winston = next((a for a in agents if a.get("name") == "Winston"), {})
if not winston:
    errors.append("missing Winston agent")
else:
    if winston.get("model") != "anthropic/claude-3.5-haiku":
        errors.append("Winston model mismatch")
    if winston.get("harness") != "Hermes":
        errors.append("Winston harness mismatch")
if errors:
    print("WINSTON KNOWLEDGE ARCHITECTURE VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("WINSTON KNOWLEDGE ARCHITECTURE VALIDATION PASSED")
