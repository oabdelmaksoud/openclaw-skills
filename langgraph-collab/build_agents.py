#!/usr/bin/env python3
"""
build_agents.py — reads each agent's SOUL.md and generates agents/ JSON configs
for langgraph-collab.

Usage:
  python3 build_agents.py            # rebuild stale only
  python3 build_agents.py --force    # rebuild all
  python3 build_agents.py --agent sage
"""

import argparse
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
AGENTS_WORKSPACES = WORKSPACE / "agents-workspaces"
SKILL_DIR = Path(__file__).parent
AGENTS_DIR = SKILL_DIR / "agents"

AGENT_DIRS = {
    "sage":   "solution-architect",
    "forge":  "implementation-engineer",
    "pixel":  "debugger",
    "vista":  "business-analyst",
    "cipher": "knowledge-curator",
    "vigil":  "quality-assurance",
    "anchor": "content-specialist",
    "lens":   "multimodal-specialist",
    "main":   ".",  # Cooper — workspace root
}

AGENT_ROLES = {
    "sage":   "Solution Architect",
    "forge":  "Implementation Engineer",
    "pixel":  "Root Cause Analyst",
    "vista":  "Business Analyst",
    "cipher": "Knowledge Curator",
    "vigil":  "Quality Assurance Engineer",
    "anchor": "Content Specialist",
    "lens":   "Multimodal Specialist",
    "main":   "Orchestrator",
}

AGENT_GOALS = {
    "sage":   "Design robust, scalable system architectures that balance complexity with maintainability",
    "forge":  "Implement clean, well-tested code that solves problems directly and efficiently",
    "pixel":  "Find the true root cause of any bug or failure, not just the symptom",
    "vista":  "Research deeply, synthesize clearly, and surface the insights that matter most",
    "cipher": "Curate, organize, and surface knowledge so the team never forgets what it has learned",
    "vigil":  "Ensure every output meets quality standards before it reaches Omar",
    "anchor": "Craft clear, compelling content that communicates complex ideas simply",
    "lens":   "Extract meaning from images, documents, and multimodal inputs with precision",
    "main":   "Orchestrate specialist agents, decompose tasks, synthesize results, and deliver outcomes to Omar",
}

AGENT_NAMES = {
    "sage": "Sage", "forge": "Forge", "pixel": "Pixel", "vista": "Vista",
    "cipher": "Cipher", "vigil": "Vigil", "anchor": "Anchor", "lens": "Lens",
    "main": "Cooper",
}

AGENT_MODELS = {
    "sage":   "anthropic/claude-sonnet-4-6",
    "forge":  "zai/glm-5",
    "pixel":  "anthropic/claude-opus-4-6",
    "vista":  "google-gemini-cli/gemini-3-pro-preview",
    "cipher": "google-gemini-cli/gemini-3-pro-preview",
    "vigil":  "zai/glm-4.7-flash",
    "anchor": "minimax-portal/MiniMax-M2.5",
    "lens":   "google-gemini-cli/gemini-3-pro-preview",
    "main":   "anthropic/claude-sonnet-4-6",
}


def extract_backstory(soul_md: str) -> str:
    match = re.search(r"##\s+Who You Are\s*\n(.*?)(?=\n##|\Z)", soul_md, re.DOTALL)
    if match:
        return match.group(1).strip()[:800]
    return soul_md[:500].strip()


def build_agent(agent_id: str, force: bool = False) -> bool:
    agent_dir = AGENT_DIRS.get(agent_id)
    if not agent_dir:
        print(f"Unknown agent: {agent_id}", file=sys.stderr)
        return False

    if agent_dir == ".":
        soul_path = WORKSPACE / "SOUL.md"
    else:
        soul_path = AGENTS_WORKSPACES / agent_dir / "SOUL.md"
    out_path = AGENTS_DIR / f"{agent_id}.json"

    if not soul_path.exists():
        print(f"Warning: {soul_path} not found, skipping {agent_id}")
        return False

    if not force and out_path.exists():
        if out_path.stat().st_mtime >= soul_path.stat().st_mtime:
            return False

    soul_md = soul_path.read_text(encoding="utf-8")
    config = {
        "agent_id":       agent_id,
        "name":           AGENT_NAMES[agent_id],
        "role":           AGENT_ROLES[agent_id],
        "goal":           AGENT_GOALS[agent_id],
        "backstory":      extract_backstory(soul_md),
        "openclaw_model": AGENT_MODELS[agent_id],
    }

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    print(f"Built agent config: {agent_id} ({AGENT_ROLES[agent_id]})")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--agent", help="Single agent to rebuild")
    args = parser.parse_args()

    agents = [args.agent] if args.agent else list(AGENT_DIRS.keys())
    rebuilt = sum(build_agent(a, force=args.force) for a in agents)
    print(f"Done. Rebuilt {rebuilt}/{len(agents)} agent configs.")


if __name__ == "__main__":
    main()
