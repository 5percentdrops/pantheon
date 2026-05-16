#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Software House V7 Workspace =="
echo "PRDs:              workspace/01_PRDs/"
echo "SDDs:              workspace/02_SDDs/"
echo "Feature tickets:  workspace/03_Feature_Tickets/"
echo "Red tests:        workspace/04_TDD_Red_Tests/"
echo "QA logs:          workspace/05_QA_Audit_Logs/"
echo "Project repos:    workspace/06_Project_Repos/"
echo "Finalization:     workspace/07_Finalization/"
echo "Master status:    workspace/MASTER_STATUS.md"
echo
echo "Run validation:"
echo "  python3 scripts/validate_v7_pipeline.py"
