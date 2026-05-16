#!/usr/bin/env python3
"""
Add person_name to every agent YAML frontmatter.
Rewrite first sentence of Personality to introduce the name.
Rewrite first sentence of Prompt Stub to use the name.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "agents"

# Name assignments by agent id
NAMES = {
    "project-manager": "Arthur",
    "senior-backend-dev": "Marcus",
    "backend-dev": "Jack",
    "senior-frontend-dev": "Sonia",
    "frontend-dev": "Leo",
    "senior-mobile-dev": "Dominic",
    "mobile-dev": "Ellie",
    "senior-mobile-designer": "Mira",
    "mobile-ui-dev": "Dante",
    "senior-devops": "Viktor",
    "devops-dev": "Theo",
    "senior-pinescript-dev": "Felix",
    "pinescript-dev": "Ben",
    "indicator-tester": "Clara",
    "senior-qa": "Nadia",
    "qa": "Ivan",
    "functional-tester": "Chloe",
    "senior-data-analyst": "Henrik",
    "data-analyst": "Elena",
    "senior-backtester": "Oscar",
    "backtester": "Atlas",
}

# Role display strings for the Prompt Stub rewrite ("You are {name}, the {role}...")
ROLE_TITLES = {
    "project-manager": "Project Manager",
    "senior-backend-dev": "Senior Backend Developer",
    "backend-dev": "Backend Developer",
    "senior-frontend-dev": "Senior Frontend Developer",
    "frontend-dev": "Frontend Developer",
    "senior-mobile-dev": "Senior Mobile Developer",
    "mobile-dev": "Mobile Developer",
    "senior-mobile-designer": "Senior Mobile Designer",
    "mobile-ui-dev": "Mobile UI Developer",
    "senior-devops": "Senior DevOps engineer",
    "devops-dev": "DevOps Developer",
    "senior-pinescript-dev": "Senior PineScript Developer",
    "pinescript-dev": "PineScript Developer",
    "indicator-tester": "Indicator Tester",
    "senior-qa": "Senior QA",
    "qa": "QA Engineer",
    "functional-tester": "Functional Tester",
    "senior-data-analyst": "Senior Data Analyst",
    "data-analyst": "Data Analyst",
    "senior-backtester": "Senior Backtester",
    "backtester": "Backtester",
}

def get_agent_id(text):
    """Extract the `id:` field from frontmatter."""
    m = re.search(r"^id:\s*(\S+)", text, re.MULTILINE)
    return m.group(1) if m else None

def add_person_name_to_frontmatter(text, name):
    """Insert `person_name: {name}` right after the `name:` line."""
    # The YAML `name:` line (CAPS display name) — insert person_name after it
    return re.sub(
        r"^(name:\s*[A-Z0-9_-]+\n)",
        r"\1person_name: " + name + "\n",
        text,
        count=1,
        flags=re.MULTILINE,
    )

def rewrite_personality_intro(text, name, agent_id):
    """Rewrite the first sentence of ## Personality to introduce the name."""
    # Find ## Personality section
    m = re.search(r"(## Personality\n\n)(.*?)(\n\n)", text, re.DOTALL)
    if not m:
        return text
    prefix, body, suffix = m.group(1), m.group(2), m.group(3)

    # Split off the first sentence (up to first period + space or period + newline)
    # The existing first sentence is a descriptor phrase — we replace with
    # "{Name} is [lowercased first sentence]."
    sentence_match = re.match(r"(.*?\.)(\s+)(.*)", body, re.DOTALL)
    if not sentence_match:
        # Single sentence — treat whole body as first sentence
        first_sentence = body
        rest = ""
    else:
        first_sentence = sentence_match.group(1)
        rest = sentence_match.group(2) + sentence_match.group(3)

    # Lowercase first letter of the first sentence so it flows after "{Name} is"
    # But handle cases where the first sentence already starts with a name-like
    # or where lowercasing would look weird. Keep it simple: "{Name} is {lowercased}"
    if first_sentence and first_sentence[0].isupper():
        lowered = first_sentence[0].lower() + first_sentence[1:]
    else:
        lowered = first_sentence

    # Special case: Atlas is a non-LLM pure-compute agent — frame accordingly
    if agent_id == "backtester":
        new_first = f"Atlas is the name of the backtest harness — a pure-compute Python service, no LLM. {first_sentence}"
    else:
        new_first = f"{name} is {lowered}"

    new_body = new_first + rest
    replacement = prefix + new_body + suffix
    return text.replace(m.group(0), replacement, 1)

def rewrite_prompt_stub(text, name, agent_id):
    """Rewrite first line of ## Prompt Stub to 'You are {name}, the {role}...'"""
    role_title = ROLE_TITLES[agent_id]

    m = re.search(r"(## Prompt Stub\n\n)(.*?)(\n\n|\Z)", text, re.DOTALL)
    if not m:
        return text
    prefix, body, suffix = m.group(1), m.group(2), m.group(3)

    # Find the existing first sentence that starts "You are..." and replace
    # with "You are {name}, the {role_title}..."
    # Pattern: "You are ... [at the Software House|of the Software House]."
    # We replace everything up to the end of that opening sentence.

    # Match "You are [...]." (first sentence)
    sent_match = re.match(r"(You are [^.]*\.)(\s+)(.*)", body, re.DOTALL)
    if not sent_match:
        return text

    original_first = sent_match.group(1)
    ws = sent_match.group(2)
    rest = sent_match.group(3)

    # Build new opening. Special case Atlas since it's not a person.
    if agent_id == "backtester":
        new_first = f"You are Atlas, the {role_title} harness at the Software House."
    elif agent_id == "project-manager":
        new_first = f"You are Arthur, the Project Manager of the Software House, running on Hermes (Opus 4.7)."
    else:
        new_first = f"You are {name}, the {role_title} at the Software House."

    new_body = new_first + ws + rest
    replacement = prefix + new_body + suffix
    return text.replace(m.group(0), replacement, 1)

def process_file(path: Path):
    text = path.read_text()
    agent_id = get_agent_id(text)
    if not agent_id:
        print(f"  SKIP {path} (no id)")
        return False
    if agent_id not in NAMES:
        print(f"  SKIP {path} (agent_id={agent_id} not in NAMES map)")
        return False

    name = NAMES[agent_id]

    # Step 1: add person_name to frontmatter
    new_text = add_person_name_to_frontmatter(text, name)

    # Step 2: rewrite personality intro
    new_text = rewrite_personality_intro(new_text, name, agent_id)

    # Step 3: rewrite prompt stub
    new_text = rewrite_prompt_stub(new_text, name, agent_id)

    path.write_text(new_text)
    print(f"  ✓ {agent_id:30s} → {name}")
    return True

def main():
    count = 0
    for md in sorted(AGENTS.glob("*/*.md")):
        if process_file(md):
            count += 1
    print(f"\nUpdated {count} agent files.")

if __name__ == "__main__":
    main()
