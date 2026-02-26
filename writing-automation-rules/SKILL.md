---
name: writing-automation-rules
description: "This skill should be used when the user asks to 'create an automation rule', 'write a process rule', 'configure automation', 'add an automation rule', or needs guidance on OpenClaw process/cron automation patterns, rule syntax, and automated enforcement."
metadata:
  {
    "openclaw":
      {
        "emoji": "📏"
      }
  }
---

# Writing Automation Rules for OpenClaw

## Overview

Automation rules in OpenClaw are patterns that define behavior enforcement, validation, and automated responses. Unlike event-driven hooks, OpenClaw uses cron jobs and process definitions to automate recurring checks, quality enforcement, and workflow orchestration.

**Key mechanisms:**
- **Cron jobs**: Scheduled recurring checks and enforcement
- **Process definitions**: Documented step-by-step workflows in PROCESSES.json
- **Quality gates**: Vigil (quality-assurance agent) rates outputs 1-5
- **Broadcast rules**: System-wide announcements via comms/broadcast.md

## Rule File Format

### Cron-Based Automation Rules

Define automated checks as cron jobs in `openclaw.json`:

```json
{
  "crons": {
    "rule-name": {
      "schedule": "*/15 * * * *",
      "agent": "quality-assurance",
      "task": "Check for violations: [describe what to check]. If found, log to FAILURES.md and notify via comms/inboxes/",
      "model": "nvidia-nim/openai/gpt-oss-120b"
    }
  }
}
```

### Process-Based Automation Rules

Define reusable workflow rules in `workspace/processes/PROCESSES.json`:

```json
{
  "id": "proc-NNN",
  "name": "Rule Name",
  "description": "What this rule enforces",
  "maturity": "L2",
  "steps": [
    "Step 1: Detect condition",
    "Step 2: Evaluate severity",
    "Step 3: Take action (warn, block, notify)",
    "Step 4: Log result"
  ],
  "owner": "quality-assurance",
  "triggers": ["When to invoke this rule"]
}
```

## Rule Types

### Validation Rules

Check for dangerous or undesirable patterns:

```json
{
  "crons": {
    "validate-no-secrets": {
      "schedule": "0 */4 * * *",
      "agent": "cybersecurity",
      "task": "Scan workspace for exposed secrets, API keys, or credentials in non-auth files. If found: (1) Log to RCA report, (2) Notify Vault via inbox, (3) Rate severity 1-5"
    }
  }
}
```

**Common validation patterns:**
- Dangerous operations (rm -rf, chmod 777)
- Exposed credentials in code or config
- Quality standard violations
- Documentation gaps

### Completion Rules

Enforce task completion standards:

```json
{
  "crons": {
    "check-task-completion": {
      "schedule": "0 */2 * * *",
      "agent": "quality-assurance",
      "task": "Review all In-Progress tickets in TASKS.json. For each: verify tests run, documentation updated, quality standards met. If incomplete after 1 hour, flag as stale."
    }
  }
}
```

### Monitoring Rules

Track system health and agent performance:

```json
{
  "crons": {
    "heartbeat-monitor": {
      "schedule": "*/5 * * * *",
      "agent": "quality-assurance",
      "task": "Check all 16 agent heartbeats. If any agent has not updated HEARTBEAT.md in > 30 minutes, log warning and notify Cooper."
    }
  }
}
```

### Enforcement Rules

Block or warn on policy violations:

Process definition approach:
```json
{
  "id": "proc-040",
  "name": "Code Quality Gate",
  "steps": [
    "Step 1: Read changed files",
    "Step 2: Check against coding standards (workspace/standards/coding.md)",
    "Step 3: Rate quality 1-5",
    "Step 4: If score < 3, block delivery and notify author agent",
    "Step 5: If score >= 3, approve and log to changelog"
  ],
  "owner": "quality-assurance"
}
```

## Pattern Writing Tips

### Task Description Best Practices

Write clear, actionable task descriptions for cron agents:

```
# GOOD: Specific, actionable, with clear outcomes
"Scan all .json files in workspace/ for syntax errors. For each error: log file path and line number to FAILURES.md, notify file owner agent via comms/inboxes/"

# BAD: Vague, no clear action
"Check for problems in the workspace"
```

### Severity Classification

| Level | Description | Action |
|-------|-------------|--------|
| 1 (Critical) | Security breach, data loss risk | Block + immediate alert |
| 2 (High) | Quality violation, broken process | Block + notify owner |
| 3 (Medium) | Standard deviation, minor issue | Warn + log |
| 4 (Low) | Style issue, suggestion | Log only |
| 5 (Info) | Observation, no action needed | Optional log |

### Common Gotchas

- **Max 1 dispatch per cron run**: Concurrent writes to tickets.json cause corruption
- **Stale session cleanup**: Gateway kills sessions after ~1 hour
- **Anthropic rate limits**: Never dispatch Anthropic-primary agents concurrently
- **IMPROVEMENT_BACKLOG.json**: Must always have >= 5 items (Vigil enforces)

## Schedule Patterns

### Crontab Syntax

```
*/5 * * * *     Every 5 minutes
0 */4 * * *     Every 4 hours
0 2 * * *       Daily at 2 AM
0 9 * * 1       Weekly Monday 9 AM
0 10 1 * *      Monthly 1st at 10 AM
0 10 1 1,4,7,10 * Quarterly
```

### Recommended Schedules by Rule Type

| Rule Type | Schedule | Agent |
|-----------|----------|-------|
| Heartbeat/health | every 5 min | Vigil |
| Quality checks | every 2-4 hours | Vigil |
| Security scans | every 4-6 hours | Vault |
| Synthesis | daily 2 AM | Cipher |
| Reports | daily 9 AM | Cooper |
| Architecture review | every 6 hours | Sage |
| Memory maintenance | every 6 hours | Cipher |

## Integration with OpenClaw Agents

### Agent-Rule Mapping

| Agent | Rule Types | Model Override |
|-------|-----------|----------------|
| Vigil (quality-assurance) | Quality gates, heartbeat, self-reflection | nvidia-nim/openai/gpt-oss-120b |
| Vault (cybersecurity) | Security scans, credential checks | anthropic/claude-sonnet-4-6 |
| Cipher (knowledge-curator) | Memory reindex, synthesis, learning | deepseek/deepseek-chat |
| Cooper (main) | Reports, OKR reviews, strategy | deepseek/deepseek-chat |
| Sage (solution-architect) | Architecture review, risk scans | minimax-portal/MiniMax-M2.5 |

### Multi-Agent Rule Chains

For complex rules that span multiple agents:

1. **Trigger agent** detects condition (cron job)
2. **Writes to inbox** of responsible agent
3. **Responsible agent** picks up from inbox on next cycle
4. **Quality gate** (Vigil) validates the response

## Enabling/Disabling Rules

### Cron Jobs
- **Disable**: Remove from openclaw.json `crons` section
- **Temporarily pause**: Add `"enabled": false` to the cron entry
- **Restart required**: Changes take effect on next gateway restart

### Processes
- **Disable**: Set maturity to "L0" (deprecated)
- **Archive**: Move to a separate `ARCHIVED_PROCESSES.json`
- **No restart needed**: Process changes are read dynamically

## Debugging Rules

### Cron Jobs
- Check gateway logs: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- Look for `embedded run start/end` entries
- Check for `disabledUntil` in auth-profiles.json
- Verify model availability and rate limits

### Processes
- Review PROCESSES.json for syntax errors
- Check CHANGELOG.md for recent modifications
- Verify owner agent exists and is configured
- Test process steps manually before automating

## Quick Reference

### Minimum Viable Cron Rule
```json
{
  "my-rule": {
    "schedule": "0 */4 * * *",
    "agent": "quality-assurance",
    "task": "Check for X. If found, log to FAILURES.md."
  }
}
```

### Minimum Viable Process Rule
```json
{
  "id": "proc-NNN",
  "name": "Rule Name",
  "maturity": "L1",
  "steps": ["Detect", "Evaluate", "Act", "Log"],
  "owner": "agent-id"
}
```
