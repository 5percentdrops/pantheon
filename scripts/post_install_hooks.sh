#!/usr/bin/env bash
set -euo pipefail
echo 'Post-install hooks placeholder.'

# V8 Paperclip staging note
mkdir -p .stage/checks
cat > .stage/checks/V8_INSTALL_BOUNDARY.md <<'EOF'
# V8 Install Boundary

This repo stages/imports a Paperclip company/org package.

It does not:
- install Paperclip
- install Hermes
- rewrite Hermes internals
- rewrite OpenClaw internals
- add production trading keys
- auto-merge code
- change governance without approval
EOF
