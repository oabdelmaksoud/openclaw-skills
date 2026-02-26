#!/usr/bin/env python3
"""
build_personas.py — reads each agent's SOUL.md and generates personas/ JSON configs.

Usage:
  python3 build_personas.py                          # rebuild stale only
  python3 build_personas.py --force                  # rebuild all
  python3 build_personas.py --agent sage             # rebuild one agent
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
AGENTS_WORKSPACES = WORKSPACE / "agents-workspaces"
SKILL_DIR = Path(__file__).parent
PERSONAS_DIR = SKILL_DIR / "personas"

# Map agent IDs to their workspace subdirectory names
AGENT_DIRS = {
    "sage":   "solution-architect",
    "forge":  "implementation-engineer",
    "pixel":  "debugger",
    "vista":  "business-analyst",
    "cipher": "knowledge-curator",
    "vigil":  "quality-assurance",
    "anchor": "content-specialist",
    "lens":   "multimodal-specialist",
}

# Map agent IDs to their OpenClaw model strings
AGENT_MODELS = {
    "sage":   "anthropic/claude-sonnet-4-6",
    "forge":  "zai/glm-5",
    "pixel":  "anthropic/claude-opus-4-6",
    "vista":  "gemini/gemini-2.0-pro-exp",
    "cipher": "gemini/gemini-2.0-pro-exp",
    "vigil":  "openai/glm-4.7-flash",
    "anchor": "openai/MiniMax-M2.5",
    "lens":   "gemini/gemini-2.0-pro-exp",
}

# LiteLLM model string mappings
LITELLM_MODELS = {
    "sage":   "anthropic/claude-sonnet-4-6",
    "forge":  "openai/glm-5",
    "pixel":  "anthropic/claude-opus-4-6",
    "vista":  "gemini/gemini-2.0-pro-exp",
    "cipher": "gemini/gemini-2.0-pro-exp",
    "vigil":  "openai/glm-4.7-flash",
    "anchor": "openai/MiniMax-M2.5",
    "lens":   "gemini/gemini-2.0-pro-exp",
}

AGENT_EMOJIS = {
    "sage":   "🔮",
    "forge":  "⚒️",
    "pixel":  "🐛",
    "vista":  "🔭",
    "cipher": "🔊",
    "vigil":  "🛡️",
    "anchor": "⚓",
    "lens":   "📡",
}

AGENT_NAMES = {
    "sage":   "Sage",
    "forge":  "Forge",
    "pixel":  "Pixel",
    "vista":  "Vista",
    "cipher": "Cipher",
    "vigil":  "Vigil",
    "anchor": "Anchor",
    "lens":   "Lens",
}


def extract_system_prompt(soul_md: str, agent_id: str, agent_name: str) -> str:
    """Extract the core persona/role section from a SOUL.md file."""
    match = re.search(
        r"##\s+Who You Are\s*\n(.*?)(?=\n##|\Z)",
        soul_md,
        re.DOTALL,
    )
    if match:
        who_you_are = match.group(1).strip()
    else:
        who_you_are = soul_md[:500].strip()

    return (
        f"You are {agent_name}, a specialist AI agent in a multi-agent system.\n\n"
        f"{who_you_are}\n\n"
        f"When collaborating with other agents:\n"
        f"- Stay in your area of expertise\n"
        f"- Be direct and specific — no filler\n"
        f"- Write ##AGREED## as a standalone line when you genuinely agree with a proposed solution\n"
        f"- Challenge weak proposals respectfully with specific technical reasoning\n"
    )


def build_persona(agent_id: str, force: bool = False) -> bool:
    """Build persona JSON for one agent. Returns True if rebuilt."""
    agent_dir_name = AGENT_DIRS.get(agent_id)
    if not agent_dir_name:
        print(f"Unknown agent: {agent_id}", file=sys.stderr)
        return False

    soul_path = AGENTS_WORKSPACES / agent_dir_name / "SOUL.md"
    persona_path = PERSONAS_DIR / f"{agent_id}.json"

    if not soul_path.exists():
        print(f"Warning: {soul_path} not found, skipping {agent_id}")
        return False

    if not force and persona_path.exists():
        if persona_path.stat().st_mtime >= soul_path.stat().st_mtime:
            return False  # up to date

    soul_md = soul_path.read_text(encoding="utf-8")
    agent_name = AGENT_NAMES[agent_id]
    system_prompt = extract_system_prompt(soul_md, agent_id, agent_name)

    persona = {
        "agent_id": agent_id,
        "name": agent_name,
        "emoji": AGENT_EMOJIS[agent_id],
        "model": AGENT_MODELS[agent_id],
        "litellm_model": LITELLM_MODELS[agent_id],
        "system_prompt": system_prompt,
    }

    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    persona_path.write_text(json.dumps(persona, indent=2, ensure_ascii=False))
    print(f"Built persona: {agent_id} ({agent_name})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build AutoGen persona configs from SOUL.md files")
    parser.add_argument("--force", action="store_true", help="Rebuild all personas")
    parser.add_argument("--agent", help="Rebuild a single agent")
    args = parser.parse_args()

    if args.agent:
        agents = [args.agent]
    else:
        agents = list(AGENT_DIRS.keys())

    rebuilt = 0
    for agent_id in agents:
        if build_persona(agent_id, force=args.force):
            rebuilt += 1

    print(f"Done. Rebuilt {rebuilt}/{len(agents)} personas.")


if __name__ == "__main__":
    main()
