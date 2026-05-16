# Rollback V8.5 → V8.4

If V8.5 (Hermes-as-harness, `hermes_local` adapter) misbehaves on your host, this is the revert path. V8.5 changes are confined to:

- `scripts/convert_to_agentcompanies_v1.py` (adapter map + per-agent env block)
- `scripts/install_to_paperclip.sh` (added `hermes --version` pre-flight)
- `scripts/install_to_hermes.sh` (now a shim → `bootstrap_hermes_homes.sh`)
- `scripts/one_click_install.sh` (added bootstrap + adapter-install steps)
- `scripts/validate_agentcompanies_v1_package.py` (added `hermes_local` to `VALID_ADAPTERS`)
- `scripts/validate_hermes_local_package.py` (NEW)
- `scripts/bootstrap_hermes_homes.{sh,py}` (NEW)
- `scripts/install_hermes_adapter_plugin.sh` (NEW)
- `scripts/validate.py` (chain now includes the new validator)
- `manifest.json` (`version`, `schema_version`, `hermes_local_adapter`, `v8_5_patch`)
- `README.md` (added "V8.5 runtime model" section)
- `PATCH_NOTES_V8_5.md` (NEW)

State written outside the repo:

- `~/.hermes-<slug>/` (32 directories)
- `~/.paperclip/adapter-plugins.json` (entry for `hermes_local`)
- Paperclip company record (`Software House`) imported via `paperclipai company import`

## Full rollback (one command, destructive)

> Removes 32 Hermes homes, the adapter plugin entry, and the imported Paperclip company. Reverts source files via `git` (assumes V8.5 commit is the most recent on the current branch).

```bash
bash scripts/rollback_to_v8_4.sh
```

If you have not yet wrapped a `rollback_to_v8_4.sh` helper, run the steps below manually.

## Manual rollback steps

### 1. Remove the imported Paperclip company

```bash
paperclipai company list                              # find the id of "Software House"
paperclipai company delete <company_id> --confirm     # deletes record + agents + skills
```

### 2. Unregister the `hermes_local` adapter plugin

```bash
node -e '
  const fs = require("fs");
  const f = process.env.HOME + "/.paperclip/adapter-plugins.json";
  if (!fs.existsSync(f)) process.exit(0);
  const d = JSON.parse(fs.readFileSync(f, "utf8"));
  d.plugins = (d.plugins || []).filter(p => p.type !== "hermes_local");
  fs.writeFileSync(f, JSON.stringify(d, null, 2) + "\n");
  console.log("Removed hermes_local entry.");
'
paperclipai restart   # reload adapters
```

### 3. Remove per-agent Hermes homes

> Destructive. Each home contains `SOUL.md`, `MEMORY.md`, sessions, and any skills the agent wrote post-task. Back up first if you care.

```bash
ls -d ~/.hermes-*                  # preview
rm -rf ~/.hermes-*                 # delete all 32 (Owen never had one)
```

To preserve memory across the rollback (recommended), back up first:

```bash
mkdir -p ~/.hermes-backup-$(date +%Y%m%d)
mv ~/.hermes-* ~/.hermes-backup-$(date +%Y%m%d)/
```

### 4. Revert source files

If the repo is under git and V8.5 was a single commit:

```bash
git log --oneline -5
git revert <V8.5_commit_sha>
```

If V8.5 spans multiple commits, prefer:

```bash
git checkout v8.4 -- scripts/ manifest.json README.md
rm -f scripts/bootstrap_hermes_homes.sh \
      scripts/bootstrap_hermes_homes.py \
      scripts/install_hermes_adapter_plugin.sh \
      scripts/validate_hermes_local_package.py \
      PATCH_NOTES_V8_5.md \
      ROLLBACK_TO_V8_4.md
```

If the repo is not under git, restore from the original V8.4 zip:

```bash
unzip -o SoftwareHouse_V8_4_OneClickInstall_RealPaperclipImport_Final_Repo.zip
```

### 5. Re-run V8.4 install (native adapters)

```bash
rm -rf software-house     # force regeneration with V8.4 adapter map
bash scripts/one_click_install.sh
```

This produces `claude_local` / `codex_local` / `gemini_local` adapter blocks for each agent.

## Partial rollbacks

### Keep V8.5 source, disable for a single agent

Edit the generated `software-house/.paperclip.yaml` for that agent — change `adapter.type: hermes_local` → `adapter.type: claude_local` (or whichever native applies). Re-import the company with `paperclipai company import --target update`.

### Keep V8.5, blow away one agent's Hermes memory

```bash
rm -rf ~/.hermes-marcus
bash scripts/bootstrap_hermes_homes.sh --only marcus --force-soul
```

### Keep V8.5, retire Owen properly (or activate)

Owen is intentionally skipped in V8.5 because NotebookLM has no API. To retire him cleanly: delete his record from the imported Paperclip company. To activate: edit `SoftwareHouse/paperclip/organization.import.json`, set Owen's `model` to a concrete provider (e.g., `google/gemini-3.1-pro`), rerun `one_click_install.sh --convert-only`, re-import.

## Verification post-rollback

```bash
paperclipai adapters list | grep -v hermes_local   # hermes_local should be gone
ls ~/.hermes-* 2>/dev/null | wc -l                 # should be 0 (or only your backup)
ls ~/.paperclip/adapter-plugins.json && grep hermes_local ~/.paperclip/adapter-plugins.json
# ^ second grep should return nothing
```
