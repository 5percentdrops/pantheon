#!/usr/bin/env bash
#
# install_hermes_adapter_plugin.sh  (V8.5)
#
# Registers the hermes_local adapter plugin with the local Paperclip server.
# Idempotent: safe to re-run.
#
# What this does:
#   1. Pre-flight: paperclipai + hermes CLIs reachable.
#   2. Ensures ~/.paperclip/adapter-plugins.json exists.
#   3. Adds or updates an entry for the hermes_local adapter package.
#   4. Tells the user to restart Paperclip (does NOT auto-restart by default).
#   5. Verifies registration via `paperclipai adapters list`.
#
# What this does NOT do:
#   - Install Paperclip itself.
#   - Install Hermes itself.
#   - Bootstrap the per-agent Hermes homes (see bootstrap_hermes_homes.sh).
#   - Import the Pantheon company (see install_to_paperclip.sh).

set -euo pipefail

# ---- Configurable ----
ADAPTER_PACKAGE="${HERMES_ADAPTER_PACKAGE:-hermes-paperclip-adapter}"
ADAPTER_VERSION="${HERMES_ADAPTER_VERSION:-^0.3.0}"
# Note: 'hermes-paperclip-adapter' (unscoped) is the OFFICIAL Nous Research
# package: github.com/NousResearch/hermes-paperclip-adapter, MIT, maintained by teknium.
# A scoped fork '@henkey/hermes-paperclip-adapter' exists at a higher version (0.4.x)
# but is a personal fork — do not substitute without auditing.
ADAPTER_TYPE="hermes_local"
PLUGINS_FILE="${PAPERCLIP_ADAPTER_PLUGINS_FILE:-$HOME/.paperclip/adapter-plugins.json}"
AUTO_RESTART="${AUTO_RESTART:-0}"

# Allow override to a file: path for local adapter dev.
# Example: HERMES_ADAPTER_PACKAGE=file:/opt/hermes-paperclip-adapter
# The script does no special handling for file: vs npm names — Paperclip's
# loader accepts both. The value is written verbatim into adapter-plugins.json.

echo "==> Pantheon V8.5 -> install hermes_local adapter plugin"
echo

# ---- Step 1: pre-flight ----
if ! command -v paperclipai >/dev/null 2>&1; then
    echo "ERROR: paperclipai CLI not found on PATH."
    echo "Install with: pnpm install -g paperclipai   (>= 2026.513.0)"
    exit 1
fi
PCLIP_VER="$(paperclipai --version 2>/dev/null || echo unknown)"
echo "paperclipai: $PCLIP_VER"

if ! command -v hermes >/dev/null 2>&1; then
    echo "ERROR: hermes CLI not found on PATH."
    echo "Install Hermes Agent first: https://github.com/NousResearch/hermes-agent"
    exit 1
fi
HERMES_VER="$(hermes --version 2>/dev/null || echo unknown)"
echo "hermes:      $HERMES_VER"

if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found on PATH (required for adapter plugin loader)."
    exit 1
fi

# ---- Step 1b: detect built-in hermes_local (Paperclip >= 2026.513.0) ----
# Paperclip ships hermes_local as a built-in adapter in current releases.
# If the live server already exposes it, no external plugin registration is
# needed and this script becomes a no-op.
API_BASE="${PAPERCLIP_API_BASE:-http://127.0.0.1:3100}"
if curl -fsS "$API_BASE/api/adapters" 2>/dev/null | grep -q '"type":"hermes_local"'; then
    echo "==> hermes_local is already loaded as a built-in adapter on $API_BASE"
    echo "    No external plugin registration needed. Exiting."
    exit 0
fi
echo "hermes_local not found in built-in adapters — proceeding with external plugin install."

# ---- Step 2: ensure plugins file exists ----
PLUGINS_DIR="$(dirname "$PLUGINS_FILE")"
mkdir -p "$PLUGINS_DIR"

if [ ! -f "$PLUGINS_FILE" ]; then
    echo "Creating $PLUGINS_FILE"
    cat > "$PLUGINS_FILE" <<EOF
{
  "plugins": []
}
EOF
fi

# ---- Step 3: idempotent add/update ----
# Use node so JSON merge survives existing entries the user may have added.
node - "$PLUGINS_FILE" "$ADAPTER_TYPE" "$ADAPTER_PACKAGE" "$ADAPTER_VERSION" <<'NODE'
const fs = require("fs");
const [, , file, type, pkg, version] = process.argv;
let doc = {};
try { doc = JSON.parse(fs.readFileSync(file, "utf8")); }
catch (e) { console.error("ERROR reading " + file + ": " + e.message); process.exit(2); }

if (!Array.isArray(doc.plugins)) doc.plugins = [];

const existing = doc.plugins.find(p => p && p.type === type);
const entry = { type, package: pkg, version };

if (existing) {
    Object.assign(existing, entry);
    console.log("Updated existing plugin entry for type=" + type);
} else {
    doc.plugins.push(entry);
    console.log("Added new plugin entry for type=" + type);
}

fs.writeFileSync(file, JSON.stringify(doc, null, 2) + "\n");
NODE

echo "Wrote: $PLUGINS_FILE"
echo

# ---- Step 4: restart guidance ----
echo "Paperclip must be restarted to load the adapter."
if [ "$AUTO_RESTART" = "1" ]; then
    echo "AUTO_RESTART=1 — attempting paperclipai restart"
    if paperclipai restart 2>/dev/null; then
        echo "Paperclip restarted."
    else
        echo "WARNING: paperclipai restart returned non-zero. Restart manually."
    fi
else
    echo "Run: paperclipai restart    (or AUTO_RESTART=1 $0)"
fi
echo

# ---- Step 5: verify ----
echo "Verifying adapter registration..."
if paperclipai adapters list 2>/dev/null | grep -q "$ADAPTER_TYPE"; then
    echo "  OK: $ADAPTER_TYPE is registered."
else
    echo "  WARNING: $ADAPTER_TYPE not yet visible to paperclipai adapters list."
    echo "  This is expected if Paperclip has not been restarted yet."
    echo "  Re-run this script after restart to re-check."
fi
echo
echo "==> Done."
