#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then PYTHON_CMD="python"; fi

echo "========================================"
echo "🚀 Starting PyMermaidView Web Interface"
echo "========================================"
echo
cat <<EOF
📋 Features:
  • Interactive Mermaid editor
  • Real-time preview
  • Multiple theme generation
  • Template library
  • Syntax validation

🌐 Opening web interface at: http://localhost:8501
💡 Press Ctrl+C to stop the server
EOF

echo "Starting Streamlit server..."
"$PYTHON_CMD" -m streamlit run streamlit_app.py
