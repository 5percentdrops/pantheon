#!/usr/bin/env bash
#
# install_to_paperclip.sh  (V8.5)
#
# Installs the Pantheon company into a local Paperclip instance.
#
# What this does:
#   1. Verifies Paperclip CLI and Hermes CLI are reachable.
#   2. Runs the V8.5 converter to produce ./pantheon/ (agentcompanies/v1)
#      with uniform hermes_local adapter blocks.
#   3. Runs `paperclipai company import --dry-run` so you see the preview.
#   4. Prompts for confirmation, then runs the real import.
#
# What this does NOT do:
#   - Install Paperclip itself (see https://github.com/paperclipai/paperclip).
#   - Install Hermes itself (see https://github.com/NousResearch/hermes-agent).
#   - Configure provider API keys (Anthropic, OpenAI, Google, OpenRouter).
#     Each Hermes home reads its own ~/.hermes-<slug>/config.yaml.
#   - Bootstrap the 32 per-agent Hermes homes — see bootstrap_hermes_homes.sh.
#   - Register the hermes_local adapter plugin — see install_hermes_adapter_plugin.sh.
#     one_click_install.sh runs all three in the right order.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_DIR="$REPO_ROOT/pantheon"
COMPANY_NAME="${COMPANY_NAME:-Pantheon}"

echo "==> Pantheon V8.5 -> Paperclip installer"
echo

# Step 1a: locate the Paperclip CLI
PAPERCLIP_CMD=""
if command -v paperclipai >/dev/null 2>&1; then
    PAPERCLIP_CMD="paperclipai"
elif command -v pnpm >/dev/null 2>&1 && pnpm paperclipai --help >/dev/null 2>&1; then
    PAPERCLIP_CMD="pnpm paperclipai"
elif command -v npx >/dev/null 2>&1; then
    PAPERCLIP_CMD="npx paperclipai"
else
    echo "ERROR: Cannot find Paperclip CLI."
    echo "Install Paperclip first:"
    echo "  pnpm install -g paperclipai"
    echo "  OR clone https://github.com/paperclipai/paperclip and run 'pnpm paperclipai run'"
    exit 1
fi
echo "Using Paperclip CLI: $PAPERCLIP_CMD"

# Step 1b: verify Hermes CLI is reachable (V8.5 requires hermes_local adapter)
if ! command -v hermes >/dev/null 2>&1; then
    echo "ERROR: Cannot find Hermes CLI on PATH."
    echo "V8.5 routes every agent through hermes_local. Install Hermes first:"
    echo "  https://github.com/NousResearch/hermes-agent"
    echo "Then verify with: hermes --version && hermes doctor"
    exit 1
fi
HERMES_VERSION="$(hermes --version 2>/dev/null || echo unknown)"
echo "Using Hermes CLI: $HERMES_VERSION"

# Step 2: check Paperclip is reachable
API_BASE="${PAPERCLIP_API_BASE:-http://localhost:3100}"
if command -v curl >/dev/null 2>&1; then
    if ! curl -fsS "$API_BASE/health" >/dev/null 2>&1 && ! curl -fsS "$API_BASE" >/dev/null 2>&1; then
        echo "WARNING: Paperclip API at $API_BASE is not reachable."
        echo "  Start it first: pnpm paperclipai run"
        echo "  Or override with: PAPERCLIP_API_BASE=https://your.host $0"
        echo
        read -p "Continue anyway? [y/N] " ans
        case "$ans" in [Yy]*) ;; *) exit 1 ;; esac
    else
        echo "Paperclip API at $API_BASE: reachable"
    fi
fi

# Step 3: run the converter
echo
echo "==> Step 1/3: Convert V8.3 payload to agentcompanies/v1 directory tree"
python3 "$REPO_ROOT/scripts/convert_to_agentcompanies_v1.py"
echo

if [ ! -d "$PKG_DIR" ]; then
    echo "ERROR: Converter did not produce $PKG_DIR"
    exit 1
fi

# Step 4: dry-run import
echo "==> Step 2/3: Dry-run import (preview only, no changes)"
echo
$PAPERCLIP_CMD company import "$PKG_DIR" \
    --target new \
    --new-company-name "$COMPANY_NAME" \
    --include company,agents,skills \
    --dry-run
echo

# Step 5: confirm + apply
echo "==> Step 3/3: Apply import"
echo "Company will be created in Paperclip as: $COMPANY_NAME"
echo "Agents to import: 33"
echo "Skills to import: 33"
echo
read -p "Apply the import? [y/N] " ans
case "$ans" in
    [Yy]*)
        $PAPERCLIP_CMD company import "$PKG_DIR" \
            --target new \
            --new-company-name "$COMPANY_NAME" \
            --include company,agents,skills \
            --yes
        echo
        echo "==> DONE. Company '$COMPANY_NAME' is now in Paperclip."
        echo
        echo "Next steps:"
        echo "  1. Open the Paperclip UI: $API_BASE"
        echo "  2. Verify hermes_local adapter is registered:"
        echo "       $PAPERCLIP_CMD adapters list | grep hermes_local"
        echo "  3. Verify 32 Hermes homes exist:"
        echo "       ls ~/.hermes-* | wc -l   # expect 32 (Owen skipped)"
        echo "  4. Configure provider API keys per Hermes home or globally in ~/.hermes/.env:"
        echo "       ANTHROPIC_API_KEY   (Anthropic provider=auto)"
        echo "       OPENAI_API_KEY      (OpenAI provider=openai-codex)"
        echo "       OPENROUTER_API_KEY  (Google/DeepSeek/Kimi via provider=openrouter)"
        echo "  5. For GitHub-touching agents, set GH_TOKEN per Hermes home."
        echo "  6. Owen has no adapter — assign a model in the Paperclip UI when ready."
        echo "  7. Set company goals + start your first project."
        ;;
    *)
        echo "Aborted. No changes applied."
        echo "The package is staged at: $PKG_DIR"
        echo "You can re-run this script or import manually:"
        echo "  $PAPERCLIP_CMD company import $PKG_DIR --target new --new-company-name '$COMPANY_NAME' --include company,agents,skills --yes"
        exit 0
        ;;
esac
