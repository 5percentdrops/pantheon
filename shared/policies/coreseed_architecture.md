# CoreSeed Architecture

Paperclip = organisation registry and route map.
Harness = agent operator and skill runtime.
Model/module = reasoning or execution engine inside the harness.
Skill = job manual, method, output contract, escalation map, and success definition.

This package installs/stages:
- Paperclip organisation definition
- agent identities
- roles
- personalities
- model/module assignments
- harness assignments
- routes/handoff paths
- Hermes seed skills
- OpenClaw seed skills

It does not try to control Hermes or OpenClaw internals.
