#!/usr/bin/env bash
set -euo pipefail

if declare -f deactivate >/dev/null 2>&1; then
  deactivate
  echo "Virtual environment deactivated."
else
  echo "No active virtual environment detected. If you used bash to activate, run: 'deactivate'"
fi
