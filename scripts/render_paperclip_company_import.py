#!/usr/bin/env python3
import json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Pantheon"

def read(path):
    return Path(path).read_text(encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=".stage/paperclip_company.import.json")
    args = ap.parse_args()

    org = json.loads((BASE / "paperclip" / "organization.import.json").read_text(encoding="utf-8"))
    routes = json.loads((BASE / "routes" / "paperclip_control_plane_routes.json").read_text(encoding="utf-8"))

    payload = {
        "kind": "paperclip_company_import",
        "version": "v8",
        "source": "Pantheon_V8_OneClickInstall_ArthurHead_PaperclipHermes",
        "organization": org.get("organization", {}),
        "control_plane": org.get("control_plane", {}),
        "hermes_runtime": org.get("hermes_runtime", {}),
        "agents": org.get("agents", []),
        "rules": org.get("rules", {}),
        "routes": routes,
        "policies": {
            "approval": read(BASE / "company" / "approval_policy.yaml"),
            "budget": read(BASE / "company" / "budget_policy.yaml"),
            "heartbeat": read(BASE / "company" / "heartbeat_policy.yaml"),
            "paperclip_control_plane": read(BASE / "policies" / "paperclip_control_plane_policy.md"),
            "hermes_harness_runtime": read(BASE / "policies" / "hermes_harness_runtime_policy.md"),
        },
        "contracts": {
            p.name: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((BASE / "contracts").glob("*.schema.json"))
        },
        "pipelines": {
            p.name: read(p)
            for p in sorted((BASE / "pipelines").glob("*.yaml"))
        },
        "install_boundary": {
            "installs_paperclip": False,
            "installs_hermes": False,
            "mutates_hermes_internals": False,
            "mutates_openclaw_internals": False,
            "stages_import_payload": True
        }
    }

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    mirror = BASE / "paperclip" / "paperclip_company.import.json"
    mirror.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"PASS: staged Paperclip company import at {out}")
    print(f"PASS: mirrored import at {mirror}")

if __name__ == "__main__":
    main()
