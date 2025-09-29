#!/usr/bin/env bash
set -euo pipefail

# Always run from project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Allow overriding via env vars; defaults mirror .bat
NAME="${GIT_USER_NAME:-SHAN Konduru}"
EMAIL="${GIT_USER_EMAIL:-ShanKonduru@gmail.com}"

echo "Configuring Git user as: $NAME <$EMAIL>"
git config --global --replace-all user.name "$NAME"
git config --global --replace-all user.email "$EMAIL"

echo "Initializing git repository (if not already initialized)..."
if [ ! -d .git ]; then
  git init
else
  echo "Git repo already initialized."
fi
