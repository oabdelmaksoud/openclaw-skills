---
name: autogen-collab
description: >
  Run multi-agent AutoGen-style debates when tasks need consensus across specialists.
  Uses OpenClaw's existing provider configuration — no API keys or extra setup needed.
  Use when: architecture decisions, design reviews, root cause analysis, or complex
  research where multiple expert perspectives improve the answer.
  Triggered automatically by Cooper for high-complexity tasks or explicitly
  via [autogen] tag or "debate this" / "get consensus" instructions.
---

# autogen-collab — Multi-Agent Debate Runner

Routes all LLM calls through `openclaw agent --json` — uses your existing
provider configuration transparently. No API keys, no venv, no .env file needed.

---

## Prerequisites (first run only)

```bash
python3 ~/.openclaw/skills/autogen-collab/build_personas.py --force
```

Run once after setup or after updating any agent's SOUL.md. The runner auto-rebuilds stale configs on each invocation, but the agents directory must exist.

## When Cooper Should Use This

### Auto-trigger (check before delegating normally)
- Task type is `architecture`, `design`, `rca`, or `research` AND complexity is `high`
- Task is tagged `[autogen]` by Omar
- Omar says "debate this", "get consensus", or "ask the team"
- Cooper's confidence on the right approach is below 70%

### Do NOT use for
- Simple, well-defined implementation tasks → delegate to Forge directly
- Tasks with a single clear owner (e.g. "write a blog post" → Anchor)
- Quick lookups or factual questions

---

## How to Invoke

### 1. Generate a task ID
```python
import uuid
task_id = str(uuid.uuid4())[:8]  # e.g. "a3f9b1c2"
```

### 2. Choose agents by task type

| Task type | Agents |
|---|---|
| `architecture` / `design` | `sage,forge,pixel` |
| `research` / `analysis` | `vista,cipher,lens` |
| `debug` / `rca` | `pixel,forge,sage` |
| `content` / `delivery` | `anchor,cipher,vigil` |
| Custom | specify explicitly |

### 3. Run the debate

```bash
python3 ~/.openclaw/skills/autogen-collab/autogen_runner.py \
  --mode debate \
  --agents sage,pixel \
  --task "Your task here" \
  --task-id "<task-id>" \
  --output /Users/omarabdelmaksoud/.openclaw/workspace/comms/autogen/<task-id>/ \
  --max-rounds 10 \
  --turn-timeout 60 \
  --timeout 300
```

Use OpenClaw's `exec` tool with `background=true` so Cooper doesn't block.

**Flags:**
- `--max-rounds` — max total agent turns (default: 10)
- `--turn-timeout` — per-turn timeout in seconds (default: 60)
- `--timeout` — total wall-clock timeout in seconds (default: 300)

### 4. Poll for completion

Every 15 seconds:
```bash
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/autogen/<task-id>/status.json
```

Continue when `status` is `complete`, `timeout`, or `error` (not `running`).

### 5. Read and route result

```bash
cat /Users/omarabdelmaksoud/.openclaw/workspace/comms/autogen/<task-id>/result.md
```

- Write result to the relevant agent outbox (`comms/outboxes/<agent>.md`)
- Send to Vigil for quality scoring (`comms/inboxes/vigil.md`)
- After Vigil approves (score ≥ 3), deliver to Omar

### 6. Log in TASKS.json

```json
{
  "autogen_session": "<task-id>",
  "transcript": "comms/autogen/<task-id>/transcript.md",
  "status": "complete"
}
```

---

## Output Files

| File | Contents |
|---|---|
| `status.json` | Run status: `running`, `complete`, `timeout`, `error` |
| `result.md` | Final answer with YAML frontmatter (task_id, agents, rounds, consensus_reached, duration_seconds) |
| `transcript.md` | Full conversation log, flushed per turn |

Status and result are **always written**, even on failure — Cooper can always check status.json.

---

## How Consensus Works

Agents receive the full conversation history each turn. When an agent genuinely
agrees with the previous response, it writes `##AGREED##` alone on a new line.
The runner detects this and ends the debate immediately.

If no consensus is reached within `--max-rounds` or `--timeout`, the runner
synthesizes the last 40 lines of transcript into `result.md` with
`consensus_reached: false`.

---

## Troubleshooting

**Agent turn times out:** Increase `--turn-timeout` or try a faster model agent.
Check if the agent's provider is responsive with `openclaw agent --agent <id> --message "ping" --json`

**Output dir already exists:** Another run used the same task ID. Generate a new UUID.

**Debate ends without consensus:** Check `transcript.md` — reduce `--max-rounds`,
simplify the task, or pick agents with closer domain alignment.

**Runner crashes before writing output:** Should not happen — status.json is written
immediately on startup. If it does, check that `openclaw` CLI is in PATH.
