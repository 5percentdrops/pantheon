#!/usr/bin/env bash
#
# one_click_install.sh — V8.6
#
# Full installer: workspace + validation + agentcompanies/v1 conversion +
# Hermes home bootstrap + hermes_local adapter plugin install +
# nightly Dreaming cron per-home + Paperclip company import.
#
# Modes:
#   bash scripts/one_click_install.sh                       # interactive
#   bash scripts/one_click_install.sh --validate-only       # validation only
#   bash scripts/one_click_install.sh --convert-only        # convert to package, no install
#   bash scripts/one_click_install.sh --no-bootstrap        # skip 32 Hermes homes
#   bash scripts/one_click_install.sh --skip-adapter-install # skip hermes_local adapter registration
#   bash scripts/one_click_install.sh --no-dreaming         # V8.6: skip nightly Dreaming cron install
#   bash scripts/one_click_install.sh --no-paperclip        # skip Paperclip import
#   bash scripts/one_click_install.sh --setup-keys          # interactive secure API key setup (opt-in)
#   bash scripts/one_click_install.sh -y                    # non-interactive, apply everything

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE_VALIDATE_ONLY=0
MODE_CONVERT_ONLY=0
SKIP_PAPERCLIP=0
SKIP_BOOTSTRAP=0
SKIP_ADAPTER_INSTALL=0
SKIP_DREAMING=0
ASSUME_YES=0
SETUP_KEYS=0

for arg in "$@"; do
    case "$arg" in
        --validate-only)        MODE_VALIDATE_ONLY=1 ;;
        --convert-only)         MODE_CONVERT_ONLY=1 ;;
        --no-paperclip)         SKIP_PAPERCLIP=1 ;;
        --no-bootstrap)         SKIP_BOOTSTRAP=1 ;;
        --skip-adapter-install) SKIP_ADAPTER_INSTALL=1 ;;
        --no-dreaming)          SKIP_DREAMING=1 ;;
        --setup-keys)           SETUP_KEYS=1 ;;
        # V8.4 back-compat: --no-hermes meant "skip the single-home skills wiring".
        # In V8.5 that step is replaced by --no-bootstrap (32 per-agent homes).
        --no-hermes)            SKIP_BOOTSTRAP=1 ;;
        -y|--yes)               ASSUME_YES=1 ;;
        -h|--help)
            sed -n '3,18p' "$0"
            exit 0
            ;;
    esac
done

echo "==================================================================="
echo " Pantheon V8.6 — Full Installer"
echo "==================================================================="
echo " Paperclip = company/control plane (the 33 agents run here)"
echo " Hermes    = per-agent harness (32 ~/.hermes-<slug>/ homes; Owen skipped)"
echo " Adapter   = hermes_local (npm: hermes-paperclip-adapter)"
echo " Arthur    = Project Manager / Head employee (openai/gpt-5-mini)"
echo "==================================================================="
echo

# Step 1: workspace
echo "==> Step 1/5: Create workspace directories"
mkdir -p \
    workspace/01_PRDs \
    workspace/02_SDDs \
    workspace/03_Feature_Tickets \
    workspace/04_TDD_Red_Tests \
    workspace/05_QA_Audit_Logs \
    workspace/06_Project_Repos \
    workspace/07_Finalization \
    workspace/08_Model_Route_Overrides \
    workspace/wiki \
    .stage

if [ ! -f "workspace/MASTER_STATUS.md" ]; then
    cp templates/MASTER_STATUS.template.md workspace/MASTER_STATUS.md 2>/dev/null || cat > workspace/MASTER_STATUS.md <<'EOT'
# MASTER_STATUS

## Active Projects

| Project | Domain | Stage | Active Ticket | Owner | Attempt | Status | Last Updated |
|---|---|---|---|---|---:|---|---|

## Project Registry

_No active projects yet._
EOT
fi
echo "  workspace ready"
echo

# Step 2: validation
echo "==> Step 2/7: Run validators"
python3 scripts/validate.py
echo

if [ "$MODE_VALIDATE_ONLY" = "1" ]; then
    echo "Validate-only mode. Exiting."
    exit 0
fi

# Step 3: legacy V8.x payload render (kept for backward compat)
echo "==> Step 3/7: Render legacy V8.x paperclip_company.import.json (backward compat)"
python3 scripts/render_paperclip_company_import.py --output .stage/paperclip_company.import.json
echo

# Step 4: V8.5 agentcompanies/v1 conversion — uniform hermes_local adapter
echo "==> Step 4/7: Convert to agentcompanies/v1 directory tree (V8.5 hermes_local)"
python3 scripts/convert_to_agentcompanies_v1.py
echo

# Step 4b: post-convert validation (validators above skip when pantheon/ absent)
echo "==> Step 4b/7: Validate generated package"
python3 scripts/validate_agentcompanies_v1_package.py
python3 scripts/validate_hermes_local_package.py
echo

if [ "$MODE_CONVERT_ONLY" = "1" ]; then
    echo "Convert-only mode. Package staged at: $ROOT/pantheon"
    exit 0
fi

bash scripts/post_install_hooks.sh 2>/dev/null || true

# Step 5: bootstrap 32 per-agent Hermes homes (V8.5 NEW)
if [ "$SKIP_BOOTSTRAP" = "0" ]; then
    echo "==> Step 5/7: Bootstrap 32 per-agent Hermes homes (~/.hermes-<slug>)"
    bash scripts/bootstrap_hermes_homes.sh --skip-doctor
    echo
else
    echo "==> Step 5/7: Skipped (--no-bootstrap)"
    echo
fi

# Step 5b: optional secure API key setup (V8.5 NEW, opt-in only via --setup-keys)
if [ "$SETUP_KEYS" = "1" ]; then
    echo "==> Step 5b/7: Interactive secure API key setup"
    echo "    (Input is hidden; values written to ~/.hermes/.env with chmod 600.)"
    bash scripts/setup_api_keys.sh
    echo
fi

# Step 6: install hermes_local adapter plugin into Paperclip (V8.5 NEW)
if [ "$SKIP_ADAPTER_INSTALL" = "0" ]; then
    echo "==> Step 6/8: Register hermes_local adapter plugin with Paperclip"
    bash scripts/install_hermes_adapter_plugin.sh
    echo
else
    echo "==> Step 6/8: Skipped (--skip-adapter-install)"
    echo
fi

# Step 6b: install nightly Dreaming cron per-home (V8.6 NEW)
if [ "$SKIP_DREAMING" = "0" ] && [ "$SKIP_BOOTSTRAP" = "0" ]; then
    echo "==> Step 7/8: Install nightly Dreaming cron in every ~/.hermes-<slug>/cron/"
    bash scripts/install_dreaming.sh
    echo
else
    echo "==> Step 7/8: Skipped (--no-dreaming or --no-bootstrap)"
    echo
fi

# Step 7b: install per-host budget watcher (V8.7 NEW, Arthur-owned)
if [ "$SKIP_DREAMING" = "0" ] && [ "$SKIP_BOOTSTRAP" = "0" ]; then
    echo "==> Step 7b/8: Install per-host budget watcher cron (Arthur-owned)"
    bash scripts/install_budget_watcher.sh
    echo
fi

# Step 7c: install Winston cross-agent dream aggregator (V8.8 NEW)
if [ "$SKIP_DREAMING" = "0" ] && [ "$SKIP_BOOTSTRAP" = "0" ]; then
    echo "==> Step 7c/8: Install Winston cross-agent dream aggregator cron"
    bash scripts/install_dream_aggregator.sh
    echo
fi

# Step 7: import company to Paperclip
echo "==> Step 8/8: Import Pantheon company to Paperclip"
echo

if [ "$SKIP_PAPERCLIP" = "0" ]; then
    if [ "$ASSUME_YES" = "1" ]; then
        ANS="y"
    else
        read -p "Import company into Paperclip now? [y/N] " ANS
    fi
    case "$ANS" in
        [Yy]*)
            if [ "$ASSUME_YES" = "1" ]; then
                yes y | bash scripts/install_to_paperclip.sh || true
            else
                bash scripts/install_to_paperclip.sh
            fi
            ;;
        *)
            echo "Skipped Paperclip import. Run manually later:"
            echo "  bash scripts/install_to_paperclip.sh"
            ;;
    esac
    echo
fi

echo "==================================================================="
echo " Install complete."
echo "==================================================================="
echo
echo " Artifacts:"
echo "   workspace/                            — local PRD/SDD/ticket tree"
echo "   .stage/paperclip_company.import.json  — legacy V8.x payload"
echo "   pantheon/                       — agentcompanies/v1 package (hermes_local)"
echo "   ~/.hermes-<slug>/                     — 32 per-agent Hermes homes"
echo "   ~/.hermes-<slug>/cron/dream.cron      — V8.6 nightly Dreaming pass (03:00 UTC)"
echo "   ~/.paperclip/adapter-plugins.json     — registers hermes_local adapter"
echo
echo " Hard rules:"
echo "   - Context pack before non-trivial work."
echo "   - Architecture before tickets."
echo "   - Tests before code."
echo "   - Green + reviewed before merge."
echo "   - Human approval for governance/merge/deploy/trading changes."
echo
echo " Next: drop a PRD into workspace/01_PRDs/[Project_Title]_PRD.md"
echo "       and let Arthur route it."
