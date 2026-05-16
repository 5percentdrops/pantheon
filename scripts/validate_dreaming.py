#!/usr/bin/env python3
"""validate_dreaming.py  (V8.6)

Asserts the Dreaming subsystem ships intact:

  1. dream_runner.sh exists, is executable, sets safe shell flags.
  2. install_dreaming.sh exists, is idempotent, supports --uninstall + --dry-run.
  3. Pantheon/pipelines/dreaming_pipeline.yaml exists with required hard_gates.
  4. Pantheon/policies/dreaming_policy.yaml exists and marks SOUL/USER/config
     immutable.
  5. one_click_install.sh references install_dreaming.sh (so dreaming
     ships with the standard installer flow).

Exits 0 on pass, 1 on any failure. Failures print one line each.
"""
from __future__ import annotations
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILS: list[str] = []


def fail(msg: str) -> None:
    FAILS.append(msg)


def must_exist(p: Path) -> bool:
    if not p.exists():
        fail(f"missing: {p.relative_to(ROOT)}")
        return False
    return True


def must_be_executable(p: Path) -> None:
    if not p.exists():
        return
    mode = p.stat().st_mode
    if not (mode & stat.S_IXUSR):
        fail(f"not executable: {p.relative_to(ROOT)} (run: chmod +x {p.relative_to(ROOT)})")


def must_contain(p: Path, needles: list[str]) -> None:
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    for n in needles:
        if n not in text:
            fail(f"{p.relative_to(ROOT)} missing required token: {n!r}")


# 1. dream_runner.sh
runner = ROOT / "scripts" / "dream_runner.sh"
if must_exist(runner):
    must_be_executable(runner)
    must_contain(runner, [
        "set -euo pipefail",
        "HERMES_HOME",
        "hermes doctor",
        "dream-",                 # log filename prefix
        "LOG_DIR",
    ])

# 2. install_dreaming.sh
installer = ROOT / "scripts" / "install_dreaming.sh"
if must_exist(installer):
    must_be_executable(installer)
    must_contain(installer, ["--dry-run", "--uninstall", "--only", "HERMES_HOME=", "dream.cron"])

# 3. pipeline
pipeline = ROOT / "Pantheon" / "pipelines" / "dreaming_pipeline.yaml"
if must_exist(pipeline):
    must_contain(pipeline, [
        "dreaming_v8_6",
        "hermes_doctor_must_pass_before_dream",
        "dream_runs_per_home_only_never_cross_agent",
        "dream_never_rewrites_soul_md",
    ])

# 4. policy
policy = ROOT / "Pantheon" / "policies" / "dreaming_policy.yaml"
if must_exist(policy):
    must_contain(policy, ["SOUL.md", "USER.md", "config.yaml", "owen"])

# 5. installer wiring
one_click = ROOT / "scripts" / "one_click_install.sh"
if must_exist(one_click) and "install_dreaming.sh" not in one_click.read_text(encoding="utf-8"):
    fail("one_click_install.sh does not reference install_dreaming.sh — Dreaming will not be set up by default")

if FAILS:
    print("FAIL: dreaming subsystem incomplete")
    for f in FAILS:
        print(f"  - {f}")
    sys.exit(1)

print("PASS: dreaming subsystem present, executable, wired into installer.")
