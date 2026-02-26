#!/usr/bin/env bash
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Setting up langgraph-collab skill..."

# Find compatible Python (langgraph requires <3.14)
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" &>/dev/null; then
    if "$candidate" -c 'import sys; assert sys.version_info < (3,14), "too new"' 2>/dev/null; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "Error: No compatible Python found (need 3.10–3.13)" >&2
  exit 1
fi

echo "Using Python: $PYTHON ($($PYTHON --version))"

if [ ! -d "$SKILL_DIR/.venv" ]; then
  echo "Creating virtual environment..."
  "$PYTHON" -m venv "$SKILL_DIR/.venv"
fi

echo "Installing langgraph..."
"$SKILL_DIR/.venv/bin/pip" install -q -r "$SKILL_DIR/requirements.txt"

mkdir -p "$SKILL_DIR/agents"
touch "$SKILL_DIR/agents/.openclaw-generated"

echo "Setup complete."
