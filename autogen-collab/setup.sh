#!/usr/bin/env bash
# autogen-collab setup — no pip install needed.
# All LLM calls route through OpenClaw's gateway (openclaw agent --json).
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "autogen-collab: no dependencies to install."
echo "Requires: python3 (stdlib only) + openclaw CLI in PATH"

# Verify openclaw is available
if ! command -v openclaw &>/dev/null; then
  echo "Error: openclaw CLI not found in PATH" >&2
  exit 1
fi

# Build personas from agent SOUL.md files
echo "Building agent personas..."
python3 "$SKILL_DIR/build_personas.py" --force

echo "Setup complete."
