#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

# Restored chain: V8.2 silently dropped most of V8.1's checks. Restore them.
# Order matters: structural Arthur check first because it catches the most
# common regression class.
validators = [
    "validate_arthur_consistency.py",
    "validate_v8_2_control_plane.py",
    "validate_v8_control_plane.py",
    "validate_v7_pipeline.py",
    "validate_caveman_full_policy.py",
    "validate_full_arthur_head_hiring.py",
    "validate_event_route_pipelines.py",
    "validate_agentcompanies_v1_package.py",
    # V8.5: uniform hermes_local adapter check
    "validate_hermes_local_package.py",
    # V8.6: mid-pipeline Nadia QA + Dreaming subsystem
    "validate_mid_pipeline_qa.py",
    "validate_dreaming.py",
    # V8.7: outcome rubric + fan-out + budget watcher + Claude MA burst + smoke ramp
    "validate_v8_7_patches.py",
    # V8.8: escalation packet schema, cross-agent dream aggregator, Maxwell override grading
    "validate_v8_8_patches.py",
]

failed = []
for v in validators:
    path = Path(__file__).with_name(v)
    if not path.exists():
        print(f"SKIP: {v} not present")
        continue
    rc = subprocess.call([sys.executable, str(path)])
    if rc != 0:
        failed.append(v)

if failed:
    print(f"\nFAILED VALIDATORS: {failed}")
    sys.exit(1)
print("\nALL VALIDATORS PASS")
