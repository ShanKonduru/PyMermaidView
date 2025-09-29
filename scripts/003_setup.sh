#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then PYTHON_CMD="python"; fi

echo "Setting up PyMermaidView project..."

echo "Upgrading pip..."
"$PYTHON_CMD" -m pip install --upgrade pip

echo "Installing Python dependencies..."
"$PYTHON_CMD" -m pip install -r requirements.txt

echo "Installing Playwright browsers for image generation..."
"$PYTHON_CMD" -m playwright install chromium

echo "Creating output and templates directories (if needed)..."
mkdir -p output templates test_reports

echo "Setup complete! You can now run:"
echo "  $PYTHON_CMD main.py                    - Run demonstrations"
echo "  $PYTHON_CMD -m src.mermaid_cli --help  - See CLI options"
echo "  pytest tests/                          - Run tests"
