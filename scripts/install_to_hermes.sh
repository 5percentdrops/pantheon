#!/usr/bin/env bash
#
# install_to_hermes.sh  (V8.5 — deprecated shim)
#
# V8.4 used this script to copy seed skills into a single shared Hermes home
# (~/.hermes). V8.5 replaces that with per-agent Hermes homes (~/.hermes-<slug>),
# one per active agent (32 homes; Owen skipped).
#
# This file is preserved as a thin shim for backward compatibility and
# delegates to bootstrap_hermes_homes.sh.

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> install_to_hermes.sh is deprecated in V8.5 — delegating to bootstrap_hermes_homes.sh"
echo "    For per-agent home isolation, prefer calling bootstrap_hermes_homes.sh directly."
echo

exec bash "$REPO_ROOT/scripts/bootstrap_hermes_homes.sh" "$@"
