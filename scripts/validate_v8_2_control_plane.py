#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SH = ROOT / "SoftwareHouse"

def fail(msg):
    print("FAIL:", msg)
    raise SystemExit(1)

def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

org = SH / "paperclip" / "organization.import.json"
if not org.exists():
    fail("missing SoftwareHouse/paperclip/organization.import.json")
data = load_json(org)

rules = data.get("rules", {})
if "arthur_model" in rules or "arthur_model_alias" in rules:
    fail("stale rules.arthur_model / rules.arthur_model_alias still present")
if data.get("hermes_runtime", {}).get("arthur_model_alias") != "openai/gpt-5-mini":
    fail("hermes_runtime.arthur_model_alias must be openai/gpt-5-mini")

arthur = next((a for a in data.get("agents", []) if a.get("id") == "arthur-project-manager"), None)
if not arthur:
    fail("arthur-project-manager missing")
if arthur.get("model") != "openai/gpt-5-mini":
    fail("Arthur agent model must be openai/gpt-5-mini")
if arthur.get("llm_module") != "GPT-5 mini under Hermes":
    fail("Arthur llm_module must be GPT-5 mini under Hermes")

for a in data.get("agents", []):
    model = a.get("model")
    if model is None:
        # null model is allowed only when model_unassigned_reason is documented
        if not a.get("model_unassigned_reason"):
            fail(f"agent {a.get('id')} has null model without model_unassigned_reason")
    elif not model:
        fail(f"agent {a.get('id')} has blank model")
    elif a.get("id") == "owen-research-pack-agent":
        # Owen workflow uses NotebookLM as a manual product; reject any synthetic
        # provider/model identifier — must be either null+reason or a real model
        if any(fake in str(model).lower() for fake in ["notebooklm/", "manual/", "custom/", "wiki/"]):
            fail(f"Owen has synthetic provider/model string: {model!r} (use null + model_unassigned_reason)")

for p in ROOT.rglob("*.md"):
    s = str(p)
    if "/deprecated/" in s or "\\deprecated\\" in s or "/source_repo/" in s or "\\source_repo\\" in s:
        continue
    if p.name.startswith("PATCH_NOTES"):
        continue
    text = p.read_text(encoding="utf-8", errors="ignore").lower()
    if "arthur" in text:
        forbidden = [
            "arthur: ops 4.7",
            "arthur | project manager | routing / pm | ops 4.7",
            "arthur | project manager | ops 4.7",
            "arthur core = deepseek",
            "default arthur core model: deepseek",
            "arthur model: sonnet 4.6",
            "anthropic/claude-sonnet-4.6"
        ]
        for needle in forbidden:
            if needle in text:
                fail(f"stale Arthur model reference in {p}: {needle}")

contracts = SH / "contracts"
for name in [
    "prd.schema.json",
    "heartbeat.schema.json",
    "transcript.schema.json",
    "budget_event.schema.json",
    "artifact_producer.schema.json",
    "model_route_override_request.schema.json",
    "merge_review.schema.json",
]:
    if not (contracts / name).exists():
        fail(f"missing contract: {name}")

merge = load_json(contracts / "merge_review.schema.json")
for field in ["reviewer_agent_id", "review_type"]:
    if field not in merge.get("required", []):
        fail(f"merge_review.schema.json missing required {field}")

routes = SH / "routes" / "paperclip_control_plane_routes.json"
r = load_json(routes)
for key in ["model_route_override_requested", "agent_heartbeat"]:
    if key not in r.get("event_routes", {}):
        fail(f"event_routes missing {key}")
for schema in ["heartbeat.schema.json", "transcript.schema.json", "budget_event.schema.json"]:
    if schema not in r.get("artifact_producers", {}):
        fail(f"artifact_producers missing {schema}")

if not (SH / "routes" / "engineering_escalation_ladder_v8_2.json").exists():
    fail("canonical engineering_escalation_ladder_v8_2.json missing")

print("PASS: V8.2 Arthur purge, contracts, producers, retry ladder, and route checks validated.")
