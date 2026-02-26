---
name: langgraph-collab
description: >
  Run stateful multi-agent graph workflows using LangGraph (linear, supervisor, parallel, conditional).
  Use when tasks need dynamic routing, branching logic, or a supervisor agent delegating work.
  All LLM calls use OpenClaw's existing provider config — no API keys needed.
  Choose over autogen-collab (debate) and crewai-collab (fixed pipelines) when you need
  conditional edges, a supervisor making routing decisions, or parallel fan-out with synthesis.
---

# langgraph-collab — Stateful Multi-Agent Graph Runner

Uses real LangGraph 0.6.11 StateGraph with shared state flowing through nodes.
Routes all LLM calls through `openclaw agent --json` — no API keys required.

## Prerequisites (first run only)

```bash
~/.openclaw/skills/langgraph-collab/setup.sh
python3 ~/.openclaw/skills/langgraph-collab/build_agents.py --force
```

## When to Use This vs. Other Skills

| Skill | Best for |
|---|---|
| `autogen-collab` | Open-ended debate, best answer wins |
| `crewai-collab` | Fixed pipeline with explicit expected outputs per task |
| `langgraph-collab` | Dynamic routing, supervisor delegation, conditional branching, parallel fan-out |

## Topology Reference

| Topology | Structure | When to use |
|---|---|---|
| `linear` | A → B → C → END | Sequential pipeline, each output feeds next |
| `supervisor` | Supervisor ⇄ workers (dynamic) | Complex task, unknown sequence upfront |
| `parallel` | All workers → synthesizer → END | Multiple expert perspectives on same task |
| `conditional` | Agent → condition check → branch A or B | If/else routing on metadata |

## Available Agents

| ID | Role |
|---|---|
| `sage` | Solution Architect |
| `forge` | Implementation Engineer |
| `pixel` | Root Cause Analyst |
| `vista` | Business Analyst |
| `cipher` | Knowledge Curator |
| `vigil` | Quality Assurance Engineer |
| `anchor` | Content Specialist |
| `lens` | Multimodal Specialist |
| `main` | Cooper (orchestrator — use as supervisor) |

## How to Invoke

### 1. Generate task ID

```python
import uuid; task_id = str(uuid.uuid4())[:8]
```

### 2. Pick topology + agents

| Goal | Topology | Agents | Supervisor |
|---|---|---|---|
| Research → Design → Implement | `linear` | `vista,sage,forge` | — |
| Complex task, dynamic routing | `supervisor` | `sage,forge,pixel` | `main` |
| Multiple expert opinions + synthesis | `parallel` | `sage,pixel,vista` | `cipher` |
| Route on condition | `conditional` | `pixel,forge` | — |

### 3. Run (use exec background=true in OpenClaw)

```bash
~/.openclaw/skills/langgraph-collab/.venv/bin/python3 \
  ~/.openclaw/skills/langgraph-collab/langgraph_runner.py \
  --topology supervisor \
  --agents sage,forge,pixel \
  --supervisor main \
  --task "Design and implement a rate limiter for the trading engine" \
  --task-id "<task-id>" \
  --output /Users/omarabdelmaksoud/.openclaw/workspace/comms/langgraph/<task-id>/ \
  --max-steps 10 \
  --turn-timeout 90 \
  --timeout 300
```

### 4. Poll for completion

```bash
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/langgraph/<task-id>/status.json
```

`status`: `running` → `complete` or `error`

### 5. Route result

```bash
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/langgraph/<task-id>/result.md
```

Route → Vigil quality gate → Omar via normal pipeline.

## Output Files (always written, even on error)

| File | Contents |
|---|---|
| `status.json` | Run status |
| `result.md` | YAML frontmatter + final graph result |
| `transcript.md` | Per-node log, flushed immediately |

## Conditional Topology

`--condition "key=value:agent_true,agent_false"`

Example — route on bug severity (Pixel sets `metadata["severity"]` in its response via `METADATA: severity=high`):

```bash
--topology conditional --agents pixel,forge,vigil \
--condition "severity=high:forge,vigil"
```

Note: agents can set metadata by including `METADATA: key=value` on its own line in their response. The runner parses this automatically and updates the shared state metadata before routing.

Example agent response:
```
I found a critical bug in the rate limiter.
METADATA: severity=high
```

## Troubleshooting

**`Agent config not found`:** Run `build_agents.py --force`

**LangGraph recursion error:** Increase `--max-steps` (default 10)

**Supervisor loops:** Check that supervisor writes `NEXT: FINISH` — simplify the task or reduce `--max-steps`

**Output dir exists:** Use a new UUID

**Slow runs:** Each node is synchronous — budget `turn-timeout × max-steps` for total time
