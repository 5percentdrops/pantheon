#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required_roles = [
    "Research Pack Agent",
    "API & Bottleneck Intelligence Agent",
    "Feasibility Strategist",
    "Skeptical Validation Agent",
    "Opportunity Architect",
    "Project Manager",
]

agents = []
for p in ROOT.rglob("organization.import.json"):
    try:
        agents.extend(json.loads(p.read_text(encoding="utf-8")).get("agents", []))
    except Exception:
        pass

roles = {a.get("role"): a for a in agents}
for role in required_roles:
    if role not in roles:
        errors.append(f"missing role: {role}")

required_files = [
    "PRD_RESEARCH_INTAKE_PIPELINE.md",
    "NOTEBOOKLM_CUSTOM_WIKI_RESEARCH_WORKFLOW.md",
    "API_BOTTLENECK_RESEARCH.md",
    "FEASIBILITY_SKEPTICISM_OPPORTUNITY_LOOP.md",
    "prd_research_intake_policy.md",
    "model_assignment_discipline_policy.md",
    "prd_approval_to_domain_routing_policy.md",
    "RESEARCH_PACK.template.md",
    "API_BOTTLENECK_REPORT.template.md",
    "FEASIBILITY_REPORT.template.md",
    "SKEPTICAL_VALIDATION_REPORT.template.md",
    "OPPORTUNITY_REPORT.template.md",
    "PRD_RESEARCH_PACKAGE.template.md",
    "prd_research_intake.schema.json",
    "api_bottleneck_report.schema.json",
    "feasibility_report.schema.json",
    "skeptical_validation_report.schema.json",
    "opportunity_report.schema.json",
    "prd_research_intake_routes.json",
]

for fname in required_files:
    if not any(p.name == fname for p in ROOT.rglob(fname)):
        errors.append(f"missing file: {fname}")

# Model discipline checks
expected_model_text = {
    "API & Bottleneck Intelligence Agent": "Gemini Pro",
    "Feasibility Strategist": "Gemini Pro",
    "Skeptical Validation Agent": "GPT-5.5",
}
for role, model_text in expected_model_text.items():
    agent = roles.get(role, {})
    if model_text not in agent.get("llm_module", ""):
        errors.append(f"{role} model mismatch: expected {model_text}")

if "Marcus" in json.dumps(json.loads(next(ROOT.rglob("prd_research_intake_routes.json")).read_text())):
    errors.append("PRD research route should not hard-default approval to Marcus")

if errors:
    print("PRD RESEARCH INTAKE VALIDATION FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("PRD RESEARCH INTAKE VALIDATION PASSED")
