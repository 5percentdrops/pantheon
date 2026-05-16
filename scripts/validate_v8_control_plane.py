#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "SoftwareHouse"

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

def load_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Invalid JSON {p}: {e}")

required = [
    "SoftwareHouse/company/paperclip_company.yaml",
    "SoftwareHouse/company/approval_policy.yaml",
    "SoftwareHouse/company/budget_policy.yaml",
    "SoftwareHouse/company/heartbeat_policy.yaml",
    "SoftwareHouse/harnesses/hermes_local.yaml",
    "SoftwareHouse/contracts/context_pack.schema.json",
    "SoftwareHouse/contracts/paperclip_issue.schema.json",
    "SoftwareHouse/contracts/model_route.schema.json",
    "SoftwareHouse/contracts/harness_assignment.schema.json",
    "SoftwareHouse/contracts/merge_review.schema.json",
    "SoftwareHouse/contracts/implementation_report.schema.json",
    "SoftwareHouse/contracts/memory_update.schema.json",
    "SoftwareHouse/contracts/ci_triage.schema.json",
    "SoftwareHouse/contracts/prd.schema.json",
    "SoftwareHouse/contracts/heartbeat.schema.json",
    "SoftwareHouse/contracts/transcript.schema.json",
    "SoftwareHouse/contracts/budget_event.schema.json",
    "SoftwareHouse/pipelines/feature_delivery_pipeline.yaml",
    "SoftwareHouse/pipelines/red_team_fanout_pipeline.yaml",
    "SoftwareHouse/pipelines/architecture_council_pipeline.yaml",
    "SoftwareHouse/pipelines/memory_hygiene_pipeline.yaml",
    "SoftwareHouse/routes/paperclip_control_plane_routes.json",
    "SoftwareHouse/policies/canonical_model_policy_v8_1.md",
    "SoftwareHouse/policies/model_route_override_policy.md",
]
missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    fail("Missing V8.1 control-plane files:\n" + "\n".join(missing))

org_path = BASE / "paperclip" / "organization.import.json"
org = load_json(org_path)
agents = org.get("agents", [])
ids = {a.get("id") for a in agents}
aliases = {
    "codex-pr-reviewer": "cody-code-escalation-reviewer",
    "paperclip-ceo": "arthur-project-manager",
    "arthur-core": "arthur-project-manager",
    "arthur-watcher": "arthur-project-manager",
}

ALLOWED_SCHEMA = {"paperclip-org-import.v8", "paperclip-org-import.v8.1", "paperclip-org-import.v8.2"}
if org.get("schema_version") not in ALLOWED_SCHEMA:
    fail(f"organization.import.json schema_version must be one of {ALLOWED_SCHEMA}, found {org.get('schema_version')!r}")

# Control-plane block supports full and mini names.
control = org.get("control_plane") or org.get("paperclip_control_plane") or {}
if not control:
    fail("Paperclip control-plane block missing")

rules = org.get("rules", {})
for key in [
    "paperclip_is_company_control_plane",
    "arthur_is_project_manager_head_employee",
    "hermes_is_harness_runtime_over_llm_models",
    "context_pack_before_non_trivial_work",
    "typed_handoffs_required",
    "governance_changes_require_human_approval",
    "production_trading_keys_forbidden_in_general_agents",
]:
    if rules.get(key) is not True:
        fail(f"Missing or false org rule: {key}")

# Active agents must be Hermes harness and must have canonical model identifiers.
harness_counts = Counter(a.get("harness") for a in agents)
if set(harness_counts) != {"Hermes"}:
    fail(f"All imported agents must use Hermes harness. Found: {dict(harness_counts)}")

for a in agents:
    aid = a.get("id")
    model = a.get("model")
    llm = a.get("llm_module")
    if model is None:
        if not a.get("model_unassigned_reason"):
            fail(f"{aid}: null model requires model_unassigned_reason")
    elif not isinstance(model, str) or not model.strip():
        fail(f"{aid}: missing canonical model field")
    if not isinstance(llm, str) or not llm.strip():
        fail(f"{aid}: missing display llm_module field")
    if aid == "arthur-project-manager" and model != "openai/gpt-5-mini":
        fail(f"Arthur model contradiction: expected openai/gpt-5-mini, found {model}")
    if aid == "arthur-project-manager" and "GPT-5 mini" not in llm:
        fail("Arthur llm_module must display GPT-5 mini under Hermes")

for aid in [
    "arthur-project-manager",
    "jack-backend-developer",
    "marcus-senior-backend-developer",
    "maxwell-staff-escalation-engineer",
    "cody-code-escalation-reviewer",
    "magnus-principal-solution-architect",
    "winston-director-knowledge-architecture",
]:
    if aid not in ids:
        fail(f"Missing canonical agent id: {aid}")

# Seed skill paths must be present and exist.
for a in agents:
    seed = a.get("seed_skill_path")
    if not seed:
        fail(f"{a.get('id')}: missing seed_skill_path")
    if "openclaw_seed" in seed.lower():
        fail(f"{a.get('id')}: active seed path must not reference OpenClaw: {seed}")
    if not (BASE / seed).exists():
        fail(f"{a.get('id')}: seed skill path does not exist: {seed}")

# Contract schemas are canonical and must include every referenced contract.
contracts = {p.name for p in (BASE / "contracts").glob("*.schema.json")}
for path in (BASE / "contracts").glob("*.schema.json"):
    load_json(path)

routes_path = BASE / "routes" / "paperclip_control_plane_routes.json"
routes = load_json(routes_path)
route_entries = routes.get("task_type_routes") or routes.get("routes") or []
for r in route_entries:
    aid = r.get("agent")
    if aid not in ids and aid not in aliases:
        fail(f"Route references unknown agent: {aid}")
    c = r.get("contract") or r.get("output_contract")
    if c and c not in contracts:
        fail(f"Route references contract not found in SoftwareHouse/contracts: {c}")

# Pipelines must be dispatchable through event_routes and their contracts must resolve.
event_routes = routes.get("event_routes") or {}
pipelines_map = routes.get("pipelines") or {}
for event in ["prd_created", "high_risk_pr_opened", "architecture_decision_requested", "weekly_memory_hygiene"]:
    if event not in event_routes:
        fail(f"Missing event route: {event}")
for pid, rel in pipelines_map.items():
    if not (ROOT / rel).exists():
        fail(f"Pipeline route {pid} points to missing file: {rel}")

for pipe in (BASE / "pipelines").glob("*.yaml"):
    txt = pipe.read_text(encoding="utf-8")
    for contract in re.findall(r"(?:output_contract|input_contract|contract):\s*([A-Za-z0-9_\-.]+\.schema\.json)", txt):
        if contract not in contracts:
            fail(f"Pipeline {pipe.name} references missing contract in contracts/: {contract}")

# Context-pack gate must be structurally enforceable.
feature = (BASE / "pipelines" / "feature_delivery_pipeline.yaml").read_text(encoding="utf-8")
if "context_pack" not in feature or "context_pack.schema.json" not in feature:
    fail("feature_delivery_pipeline must start with/require context pack")
if "context_pack_required_before" not in json.dumps(routes):
    fail("routes must declare context_pack_required_before gate")

# No active OpenClaw runtime material may remain in active policy/skill paths.
for forbidden in [BASE / "skills" / "openclaw_seed", BASE / "policies" / "openclaw_escalation_policy.md", BASE / "shared" / "policies" / "openclaw_escalation_policy.md"]:
    if forbidden.exists():
        fail(f"Active OpenClaw material remains: {forbidden.relative_to(ROOT)}")

# Budget policy sanity without requiring YAML dependency.
budget = (BASE / "company" / "budget_policy.yaml").read_text(encoding="utf-8")
cap_match = re.search(r"default_monthly_cap_usd:\s*(\d+)", budget)
if not cap_match:
    fail("budget_policy.yaml missing default_monthly_cap_usd")
global_cap = int(cap_match.group(1))
section = re.search(r"per_agent_caps(?:_usd)?:\n(?P<body>(?:\s{4}[A-Za-z0-9_-]+:\s*\d+\n)+)", budget)
if not section:
    fail("budget_policy.yaml missing per-agent caps")
per_sum = sum(int(x) for x in re.findall(r":\s*(\d+)\s*$", section.group('body'), flags=re.M))
if per_sum > global_cap:
    fail(f"Per-agent caps exceed global monthly cap: {per_sum} > {global_cap}")

print("PASS: V8.1 Paperclip control-plane layer validated.")
print("PASS: Canonical model fields populated and Arthur model collapsed.")
print("PASS: Contracts directory is canonical and route/pipeline references resolve.")
print("PASS: Pipelines are dispatchable via event_routes.")
print("PASS: Context-pack gate, budget sanity, and OpenClaw deactivation validated.")
