# openclaw-skills

Custom [OpenClaw](https://openclaw.ai) skills for Cooper's 9-agent AI system.

## What's here

| Skill | Description |
|-------|-------------|
| `autogen-collab` | AutoGen-style round-robin debate runner — agents debate until consensus (`##AGREED##`). Routes all LLM calls through OpenClaw gateway, no API keys needed. |
| `crewai-collab` | CrewAI 1.9.3 structured task runner (sequential / hierarchical / consensus). Role-based agents with explicit task expected outputs. |
| `brainstorming` | Explore user intent and design before any implementation. |
| `dispatching-parallel-agents` | Dispatch 2+ independent tasks as parallel subagents. |
| `executing-plans` | Execute a written implementation plan in a separate session with review checkpoints. |
| `finishing-a-development-branch` | Guides completion of development work (merge, PR, or cleanup). |
| `frontend-design` | Create distinctive, production-grade frontend interfaces. |
| `requesting-code-review` | Dispatch code-reviewer subagent after completing features. |
| `receiving-code-review` | Handle incoming code review feedback with rigor. |
| `subagent-driven-development` | Execute plans task-by-task with fresh subagents + two-stage review. |
| `systematic-debugging` | Structured debugging approach before proposing fixes. |
| `test-driven-development` | TDD workflow for features and bugfixes. |
| `using-git-worktrees` | Isolated git worktrees for feature work. |
| `verification-before-completion` | Verify work actually works before claiming it's done. |
| `writing-plans` | Write implementation plans before touching code. |
| `writing-automation-rules` | Create OpenClaw process/cron automation patterns. |
| `writing-skills` | Create and verify new OpenClaw skills. |
| `skill-creator` | Create, modify, and measure skill performance. |
| `openclaw-*` | OpenClaw workspace, settings, agent, command, hook development guides. |
| `hf-*` / `hugging-face-*` | Hugging Face Hub integrations (models, datasets, jobs, training, evaluation). |
| `mcp-integration` | Integrate MCP servers into OpenClaw. |
| `playground` | Create interactive HTML playgrounds. |
| `stripe-best-practices` | Stripe integration best practices. |
| `example-skill` | Reference template for creating new skills. |

## Setup

Skills are installed globally at `~/.openclaw/skills/`. OpenClaw picks them up automatically.

```bash
# Clone into your skills directory
git clone https://github.com/oabdelmaksoud/openclaw-skills ~/.openclaw/skills

# For crewai-collab: install dependencies
~/.openclaw/skills/crewai-collab/setup.sh

# Build agent configs (crewai-collab + autogen-collab)
python3 ~/.openclaw/skills/crewai-collab/build_agents.py --force
python3 ~/.openclaw/skills/autogen-collab/build_personas.py --force
```

## Architecture: autogen-collab + crewai-collab

Both skills route LLM calls through OpenClaw's gateway — no `.env` or API keys needed:

```
Cooper (orchestrator)
  └─ exec: python3 autogen_runner.py / crewai_runner.py
       └─ per turn: openclaw agent --agent <id> --message <text> --json
            └─ OpenClaw gateway → provider (Anthropic / Gemini / ZAI / MiniMax)
```

Output always written to `comms/autogen/<task-id>/` or `comms/crewai/<task-id>/`:
- `status.json` — run status
- `result.md` — final answer with YAML frontmatter
- `transcript.md` — full conversation log

## License

MIT
