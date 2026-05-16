# V8 Patch Notes — Paperclip + Hermes Corrected Software House

## Summary

This patch upgrades the existing Software House V7 repo into a V8 Paperclip/Hermes control-plane package.

It preserves the V7 operating model:

- Arthur as Project Manager / Head
- Hermes-only standard harness
- DeepSeek V4 Pro standard developers
- Opus 4.7 XHigh senior developers
- Opus 4.7 Max Maxwell escalation
- Cody code escalation reviewer
- Magnus Gemini Pro 3.1 architecture rethink
- Winston knowledge/archive layer
- PRD -> SDD -> Tickets -> TDD -> PR -> Review -> Merge gate

It adds the corrected Paperclip/Hermes architecture:

```text
Paperclip = company/control plane
Arthur = Project Manager / Head employee inside Paperclip
Hermes = harness/runtime over selected LLM models
LLM models = GPT-5 mini, GPT-5.5, Opus 4.7 XHigh/Max, Gemini Pro 3.1, DeepSeek V4 Pro, etc.
```

## Added

- `SoftwareHouse/company/`
  - `paperclip_company.yaml`
  - `approval_policy.yaml`
  - `budget_policy.yaml`
  - `heartbeat_policy.yaml`

- `SoftwareHouse/harnesses/`
  - `hermes_local.yaml`
  - `codex_repo_worker.yaml`

- `SoftwareHouse/contracts/`
  - `context_pack.schema.json`
  - `paperclip_issue.schema.json`
  - `model_route.schema.json`
  - `harness_assignment.schema.json`
  - `merge_review.schema.json`
  - `implementation_report.schema.json`
  - `memory_update.schema.json`
  - `ci_triage.schema.json`

- `SoftwareHouse/pipelines/`
  - `feature_delivery_pipeline.yaml`
  - `red_team_fanout_pipeline.yaml`
  - `architecture_council_pipeline.yaml`
  - `memory_hygiene_pipeline.yaml`

- `SoftwareHouse/routes/paperclip_control_plane_routes.json`
- `SoftwareHouse/policies/paperclip_control_plane_policy.md`
- `SoftwareHouse/policies/hermes_harness_runtime_policy.md`
- `docs/PAPERCLIP_HERMES_CONTROL_PLANE_V8.md`
- `scripts/validate_v8_control_plane.py`
- `scripts/render_paperclip_company_import.py`
- `SoftwareHouse/paperclip/paperclip_company.import.json`

## Changed

- `scripts/one_click_install.sh` is now the canonical V8 installer.
- `scripts/install.sh` is now a compatibility wrapper around the V8 installer.
- `scripts/validate.py` no longer uses the stale V7-only seed validator; it runs V7 + V8 validators.
- `SoftwareHouse/paperclip/organization.import.json` now uses `paperclip-org-import.v8`.
- `manifest.json` now states Paperclip as control plane and Hermes as harness/runtime.
- `README_INSTALL.md` and `ONE_CLICK_INSTALL.md` now document V8.

## Fixed

- Old `scripts/validate.py` failure caused by Winston missing `seed_skill_path`.
- Cody canonical ID drift:
  - canonical: `cody-code-escalation-reviewer`
  - compatibility alias: `codex-pr-reviewer`
- OpenClaw is no longer counted as an active standard harness.
- The old installer no longer installs OpenClaw seed skills as active harness seeds.

## Validation

Validated successfully with:

```bash
bash scripts/one_click_install.sh
bash scripts/install.sh
```

Both return exit code `0`.

Note: the environment emitted unrelated spreadsheet runtime warmup warnings from the container Python startup hook. The Software House validators passed and the shell commands exited successfully.
