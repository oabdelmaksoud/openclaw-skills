---
name: openclaw-hook-development
description: "This skill should be used when the user asks to 'create a cron job', 'add a scheduled task', 'write a process definition', 'configure automation', 'set up event-driven automation', 'define a process in PROCESSES.json', or needs guidance on OpenClaw cron jobs (`openclaw cron`), process definitions, scheduled automation, or workflow automation best practices."
metadata:
  {
    "openclaw":
      {
        "emoji": "🪝"
      }
  }
---

# Automation Development for OpenClaw

## Overview

OpenClaw uses two primary automation mechanisms: **cron jobs** for scheduled recurring tasks and **process definitions** for documented workflows. These replace traditional event-driven hooks with a file-based orchestration approach.

**Key capabilities:**
- Schedule recurring agent tasks with `openclaw cron`
- Define reusable processes in `workspace/processes/PROCESSES.json`
- Enforce quality gates and completion standards
- Automate synthesis, monitoring, and maintenance workflows

## Cron Jobs (Scheduled Automation)

### What are OpenClaw Cron Jobs?

Cron jobs are scheduled tasks that run agents at specified intervals. Each cron job:
- Targets a specific agent from the 16-agent roster
- Runs with `--no-deliver --session isolated` (sandboxed, no chat window)
- Executes on a defined schedule (crontab syntax or natural language)
- Can override the agent's default model

### Cron Job Configuration

Cron jobs are defined in `openclaw.json` under the `crons` section:

```json
{
  "crons": {
    "job-name": {
      "schedule": "*/5 * * * *",
      "agent": "agent-id",
      "task": "Task description for the agent",
      "model": "provider/model-override",
      "options": {
        "no-deliver": true,
        "session": "isolated"
      }
    }
  }
}
```

### Critical Cron Rules

1. **Always use `--no-deliver`**: Even best-effort with no chat window records error status
2. **Always use `--session isolated`**: Sandboxed, fresh context per run
3. **Model overrides**: Use fast/unlimited models for cron agents (e.g., `deepseek/deepseek-chat` for Cooper crons, `nvidia-nim/openai/gpt-oss-120b` for Vigil crons)
4. **Max 1 dispatch per cron run**: Concurrent dispatch causes race conditions on tickets.json
5. **Never dispatch Anthropic-primary agents concurrently**: They share OAuth subscription limits

### Common Cron Patterns

| Pattern | Schedule | Agent | Purpose |
|---------|----------|-------|---------|
| Heartbeat | every 5 min | Vigil | System health monitoring |
| Synthesis | daily 2 AM | Cipher | Knowledge consolidation |
| Self-reflection | every 3 hours | Vigil | Process quality assessment |
| System health | every 6 hours | Sage | Architecture review |
| Daily report | 9 AM | Cooper | Status compilation |
| Memory reindex | every 6 hours | Cipher | LanceDB memory maintenance |

### Creating a New Cron Job

```bash
openclaw cron add \
  --name "my-new-cron" \
  --schedule "0 */4 * * *" \
  --agent "agent-id" \
  --task "Description of what the agent should do" \
  --model "deepseek/deepseek-chat" \
  --no-deliver \
  --session isolated
```

## Process Definitions (Documented Workflows)

### What are Processes?

Processes are documented, repeatable workflows stored in `workspace/processes/PROCESSES.json`. They define how specific operations should be executed, with maturity levels tracking adoption.

### Process Structure

```json
{
  "processes": [
    {
      "id": "proc-001",
      "name": "Process Name",
      "description": "What this process accomplishes",
      "maturity": "L2",
      "steps": [
        "Step 1: Description",
        "Step 2: Description",
        "Step 3: Description"
      ],
      "owner": "agent-id",
      "triggers": ["When to invoke this process"],
      "outputs": ["What this process produces"]
    }
  ]
}
```

### Maturity Levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Ad Hoc | Process identified but not documented |
| L2 | Documented | Steps written down, ready for use |
| L3 | Practiced | Used 3+ times, proven effective |
| L4 | Optimized | Measured, refined, continuously improved |

### Creating a New Process

1. Define the process purpose and trigger conditions
2. Document step-by-step workflow
3. Assign an owner agent
4. Add to `PROCESSES.json` at L1 maturity
5. Document in `workspace/processes/CHANGELOG.md`
6. Promote to L2 after full documentation
7. Track usage — promote to L3 after 3+ successful uses

## Quality Gate Integration

### Vigil Quality Gate

All automation outputs pass through Vigil's quality gate:
- Rating 1-5 scale
- Score >= 3: Delivers to user
- Score < 3: Blocks and requests revision

### Implementing Quality Checks in Cron Jobs

```json
{
  "task": "Run quality assessment. Rate output 1-5. If score < 3, log to FAILURES.md and notify agent via comms/inboxes/"
}
```

## Automation vs. Process Decision Guide

| Need | Use Cron Job | Use Process Definition |
|------|-------------|----------------------|
| Recurring schedule | Yes | No |
| One-time workflow | No | Yes |
| Monitoring/health | Yes | No |
| Complex multi-step | No | Yes |
| Agent-driven | Yes | Either |
| User-triggered | No | Yes |

## Best Practices

### Cron Jobs
- Use fast, unlimited models (DeepSeek, NIM GPT-OSS) for cron agents
- Never exceed 1 concurrent dispatch per cron run
- Stagger Anthropic-primary agents by 120s minimum
- Monitor for stale sessions (gateway kills after ~1 hour)
- Log results to agent workspaces, not stdout

### Processes
- Start at L1, promote through maturity levels based on usage
- Record all process changes in CHANGELOG.md
- Keep IMPROVEMENT_BACKLOG.json at >= 5 items (Vigil enforces)
- Use RACI matrix for complex multi-agent processes

## Debugging Automation

### Cron Job Issues
- Check gateway logs: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- Verify agent auth profiles have valid keys
- Check for `disabledUntil` fields in auth-profiles.json (DeepSeek cooldown)
- Monitor `embedded run start/end` entries in logs

### Process Issues
- Verify process exists in PROCESSES.json
- Check maturity level (L1 may not be fully documented)
- Review CHANGELOG.md for recent modifications
- Check owner agent's inbox for stuck tasks

## Additional Resources

### Reference Files
- **`references/patterns.md`** — Common automation patterns and templates
- **`references/advanced.md`** — Advanced cron job configurations and multi-agent orchestration

### Utility Scripts
- **`scripts/validate-cron.sh`** — Validate cron job configuration syntax
