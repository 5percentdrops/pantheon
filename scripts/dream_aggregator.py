#!/usr/bin/env python3
"""dream_aggregator.py  (V8.8) — Winston-owned cross-agent learning

Runs nightly at 04:00 UTC, AFTER all per-agent Dreams complete at 03:00.
Scrapes every ~/.hermes-<slug>/logs/dream-*.log and ~/.hermes-<slug>/skills/*.md
from the last 24h, extracts patterns, dedups across agents, and writes
a single workspace/wiki/lessons_learned.md that Jack (and any engineer)
pre-reads before starting a new TDD loop.

This is the cross-agent compounding layer V8.6 deliberately omitted.
V8.6 dreaming kept agents isolated; V8.8 lets Winston lift patterns up
to org level.

Invariants:
  - Read-only across all ~/.hermes-* homes EXCEPT ~/.hermes-winston
    (Winston owns the aggregate and may write to his own home + the wiki)
  - SOUL.md / USER.md / config.yaml never read or rewritten
  - Aggregate is append-deduped; never deletes prior lessons (auditability)
  - Pure file IO + sha256; no LLM call (Winston's reasoning runs at
    dispatch time, not in the aggregator)
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI = REPO_ROOT / "workspace" / "wiki"
LESSONS = WIKI / "lessons_learned.md"
INDEX = WIKI / "lessons_learned.index.json"
HOME = Path.home()

WINDOW_HOURS = 24
MAX_SKILL_BYTES_PER_AGENT = 50_000

PATTERN_HINTS = [
    re.compile(r"(?:bug|issue|failure)\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"(?:lesson|takeaway|insight)\s*:\s*(.+)", re.IGNORECASE),
    re.compile(r"(?:do\s*not|avoid|never)\s+(.+)", re.IGNORECASE),
    re.compile(r"(?:always|must)\s+(.+)", re.IGNORECASE),
]


def hash_lesson(text: str) -> str:
    norm = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]


def collect_skill_bodies(home: Path) -> list[tuple[str, str]]:
    skills = home / "skills"
    if not skills.exists():
        return []
    out = []
    bytes_used = 0
    for f in sorted(skills.rglob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        bytes_used += len(text.encode("utf-8"))
        if bytes_used > MAX_SKILL_BYTES_PER_AGENT:
            break
        out.append((f.name, text))
    return out


def collect_recent_dream_logs(home: Path) -> list[str]:
    logs_dir = home / "logs"
    if not logs_dir.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)
    out = []
    for f in sorted(logs_dir.glob("dream-*.log")):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, timezone.utc)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        try:
            out.append(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return out


def extract_lessons(text: str) -> list[str]:
    found = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 12 or len(line) > 400:
            continue
        for pat in PATTERN_HINTS:
            m = pat.search(line)
            if m:
                fragment = m.group(1).strip().rstrip(".")
                if fragment and fragment.lower() not in {"none", "nothing"}:
                    found.append(fragment)
                break
    return found


def main() -> int:
    homes = sorted(p for p in HOME.glob(".hermes-*") if p.is_dir())
    if not homes:
        print("dream_aggregator: no ~/.hermes-* homes present", file=sys.stderr)
        return 1

    WIKI.mkdir(parents=True, exist_ok=True)

    index: dict[str, dict] = {}
    if INDEX.exists():
        try:
            index = json.loads(INDEX.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            index = {}

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_count = 0
    for home in homes:
        slug = home.name.removeprefix(".hermes-")
        sources: list[str] = []
        sources.extend(collect_recent_dream_logs(home))
        for _name, body in collect_skill_bodies(home):
            sources.append(body)

        for src in sources:
            for lesson in extract_lessons(src):
                key = hash_lesson(lesson)
                if key in index:
                    # bump last-seen + agent provenance
                    if slug not in index[key]["agents"]:
                        index[key]["agents"].append(slug)
                    index[key]["last_seen_utc"] = now_iso
                else:
                    index[key] = {
                        "id": key,
                        "lesson": lesson,
                        "agents": [slug],
                        "first_seen_utc": now_iso,
                        "last_seen_utc": now_iso,
                    }
                    new_count += 1

    # Write deterministic markdown
    lines = [
        "# Pantheon Lessons Learned",
        "",
        "_Auto-generated by `scripts/dream_aggregator.py` (V8.8) — Winston-owned cross-agent learning._",
        "_Pre-read by engineers before starting a new TDD loop._",
        "",
        f"_Last aggregation: {now_iso} UTC. Total lessons: {len(index)}._",
        "",
        "| ID | Lesson | First seen by | Reinforced by |",
        "|---|---|---|---|",
    ]
    for entry in sorted(index.values(), key=lambda e: (-len(e["agents"]), e["first_seen_utc"])):
        lesson_safe = entry["lesson"].replace("|", "\\|")
        first_agent = entry["agents"][0]
        reinforcing = ", ".join(sorted(set(entry["agents"][1:]))) or "—"
        lines.append(f"| `{entry['id']}` | {lesson_safe} | {first_agent} | {reinforcing} |")

    LESSONS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    INDEX.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")

    print(f"dream_aggregator: {len(homes)} homes scanned, "
          f"{new_count} new lessons, {len(index)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
