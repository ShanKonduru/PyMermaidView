#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then PYTHON_CMD="python"; fi

echo "Creating virtual environment in .venv using $PYTHON_CMD..."
"$PYTHON_CMD" -m venv .venv

echo "Done. Activate with: source .venv/bin/activate"
