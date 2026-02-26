#!/usr/bin/env bash
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Setting up crewai-collab skill..."

# crewai requires Python >=3.10,<3.14. Use python3.13 if available, else python3.
PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON_BIN="$(command -v "$candidate")"
    break
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi
echo "Using Python: $PYTHON_BIN ($($PYTHON_BIN --version))"

# Create venv with compatible python
if [ ! -d "$SKILL_DIR/.venv" ]; then
  echo "Creating virtual environment..."
  "$PYTHON_BIN" -m venv "$SKILL_DIR/.venv"
fi

echo "Installing crewai..."
"$SKILL_DIR/.venv/bin/pip" install -q -r "$SKILL_DIR/requirements.txt"

# Create agents dir with marker
mkdir -p "$SKILL_DIR/agents"
touch "$SKILL_DIR/agents/.openclaw-generated"

echo "Setup complete."
