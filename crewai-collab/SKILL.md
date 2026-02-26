---
name: crewai-collab
description: >
  Run structured multi-agent workflows using CrewAI (sequential, hierarchical, consensus).
  Each agent has a defined role, goal, and backstory. Tasks have explicit expected outputs.
  Use when: structured pipelines (research → design → implement), manager-supervised workflows,
  or consensus-building with clear acceptance criteria.
  All LLM calls use OpenClaw's existing provider config — no API keys needed.
---

# crewai-collab — Structured Multi-Agent Task Runner

Uses real CrewAI 1.9.3 orchestration with role-based agents and typed tasks.
Routes all LLM calls through `openclaw agent --json` — no API keys required.

**Use this (not autogen-collab) when:**
- Tasks have a clear pipeline structure (research → design → implement)
- You need explicit expected outputs per task ("return a class diagram")
- You want a manager agent (Cooper/main) reviewing and delegating each step
- Tasks have defined acceptance criteria

**Use autogen-collab instead when:**
- Open-ended debate with no fixed structure
- You just need the best answer, not a specific artifact format

---

## Prerequisites (first run only)

```bash
python3 ~/.openclaw/skills/crewai-collab/build_agents.py --force
```

Run once after setup or after updating any agent's SOUL.md. The runner auto-rebuilds stale configs on each invocation, but the agents directory must exist.

## Process Types

| Process | How it works | When to use |
|---|---|---|
| `sequential` | Each task runs in order; each agent's output feeds the next | Pipelines with clear A→B→C flow |
| `hierarchical` | Manager (Cooper/main agent) delegates, reviews, approves each task | Complex tasks needing oversight |
| `consensus` | All agents work toward a shared expected output (sequential + consensus prompt) | When you need agreement, not just output |

---

## Available Agents

| ID | Role | Best for |
|---|---|---|
| `sage` | Solution Architect | Architecture, system design, ADRs |
| `forge` | Implementation Engineer | Code, scripts, implementation |
| `pixel` | Root Cause Analyst | Debugging, RCA, failure analysis |
| `vista` | Business Analyst | Research, requirements, analysis |
| `cipher` | Knowledge Curator | Memory synthesis, knowledge management |
| `vigil` | Quality Assurance Engineer | Review, validation, quality checks |
| `anchor` | Content Specialist | Documentation, reports, formatting |
| `lens` | Multimodal Specialist | Images, documents, multimodal inputs |

---

## How to Invoke

### 1. Generate a task ID
```python
import uuid; task_id = str(uuid.uuid4())[:8]
```

### 2. Choose agents + process

| Pipeline type | Agents | Process |
|---|---|---|
| Research → Design → Review | `vista,sage,pixel` | `sequential` |
| Research → Design → Implement | `vista,sage,forge` | `sequential` |
| Complex task with oversight | `sage,forge` | `hierarchical` |
| Architecture consensus | `sage,pixel,forge` | `consensus` |
| Quality gate review | `vigil,sage` | `sequential` |

### 3. Run the crew (background process)

```bash
~/.openclaw/skills/crewai-collab/.venv/bin/python3 \
  ~/.openclaw/skills/crewai-collab/crewai_runner.py \
  --process sequential \
  --agents vista,sage,forge \
  --tasks "Research|Research the problem domain and identify key constraints|Summary with 5 key findings and constraints" \
          "Design|Design a solution architecture based on the research findings|Architecture spec with component diagram" \
          "Implement|Write a Python implementation of the designed architecture|Working Python module with docstrings" \
  --task-id "<task-id>" \
  --output /Users/omarabdelmaksoud/.openclaw/workspace/comms/crewai/<task-id>/ \
  --turn-timeout 90 \
  --timeout 300
```

Use OpenClaw's `exec` tool with `background=true` so Cooper doesn't block.

### 4. Poll for completion

Every 15–30 seconds:
```bash
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/crewai/<task-id>/status.json
```

`status` values: `running` → `complete` or `error`

### 5. Read and route result

```bash
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/crewai/<task-id>/result.md
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/crewai/<task-id>/transcript.md
```

- Write result to relevant agent outbox (e.g. `comms/outboxes/sage.md`)
- Send to Vigil for quality scoring
- After Vigil approves, deliver to Omar via normal pipeline

### 6. Log in TASKS.json

Update the task entry:
- `crewai_session`: `<task-id>`
- `transcript`: `comms/crewai/<task-id>/transcript.md`
- `status`: `complete`

---

## Output Files (always written, even on error)

| File | Contents |
|---|---|
| `status.json` | Run status: `running` / `complete` / `error` |
| `result.md` | YAML frontmatter + CrewAI final output |
| `transcript.md` | Per-task agent log, flushed immediately |

---

## Task Spec Format

Each `--tasks` argument: `"Title|Description|Expected output"`

- **Title**: Short label (for transcript)
- **Description**: What the agent must do (be specific)
- **Expected output**: What a good answer looks like (be concrete — this is what CrewAI optimizes for)

Good expected output examples:
- `"A numbered list of exactly 3 risks with one-sentence explanations"`
- `"A Python class with docstring, __init__, and at least 2 methods"`
- `"APPROVED or a list of specific issues found"`

---

## Troubleshooting

**`Agent config not found`:** Run `python3 ~/.openclaw/skills/crewai-collab/build_agents.py --force`

**Agent turn times out:** Increase `--turn-timeout` (default 90s). Test provider: `openclaw agent --agent <id> --message "ping" --json --timeout 30`

**`Output directory already exists`:** Generate a new task UUID — never reuse task IDs.

**`hierarchical` process errors:** Some crewai versions require `manager_agent` instead of `manager_llm`. Fall back to `sequential` if hierarchical fails.

**Slow run:** Sequential runs are synchronous — each task waits for the prior one. For a 3-task run with 90s per turn, expect up to 5 minutes total.
