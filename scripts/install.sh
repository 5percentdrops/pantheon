#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper.
# V8 canonical installer is scripts/one_click_install.sh.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash scripts/one_click_install.sh

INSTALL_ROOT="${SOFTWAREHOUSE_INSTALL_ROOT:-$HOME/softwarehouse}"
PAPERCLIP_IMPORT_DIR="${PAPERCLIP_IMPORT_DIR:-$HOME/paperclip/imports/SoftwareHouse}"
HERMES_SEED_DIR="${HERMES_SEED_DIR:-$HOME/hermes/seed_skills/SoftwareHouse}"

mkdir -p "$INSTALL_ROOT" "$PAPERCLIP_IMPORT_DIR" "$HERMES_SEED_DIR"

cp .stage/paperclip_company.import.json "$PAPERCLIP_IMPORT_DIR/" 2>/dev/null || true
cp SoftwareHouse/paperclip/organization.import.json "$PAPERCLIP_IMPORT_DIR/" 2>/dev/null || true
cp SoftwareHouse/paperclip/agents.json "$PAPERCLIP_IMPORT_DIR/" 2>/dev/null || true
cp SoftwareHouse/paperclip/agents.csv "$PAPERCLIP_IMPORT_DIR/" 2>/dev/null || true
cp SoftwareHouse/routes/routes.json "$PAPERCLIP_IMPORT_DIR/" 2>/dev/null || true
cp SoftwareHouse/routes/paperclip_control_plane_routes.json "$PAPERCLIP_IMPORT_DIR/" 2>/dev/null || true

cp -R SoftwareHouse/skills/hermes_seed/* "$HERMES_SEED_DIR/" 2>/dev/null || true
cp -R SoftwareHouse "$INSTALL_ROOT/" 2>/dev/null || true
cp -R shared "$INSTALL_ROOT/shared" 2>/dev/null || true

echo "SoftwareHouse V8 staged successfully."
echo "Note: OpenClaw seed install is intentionally not performed. Hermes remains the standard harness."
