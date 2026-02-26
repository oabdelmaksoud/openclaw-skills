---
name: dispatching-parallel-agents
description: Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
metadata:
  {
    "openclaw":
      {
        "emoji": "⚡"
      }
  }
---

# Dispatching Parallel Agents

## Overview

When you have multiple unrelated failures (different test files, different subsystems, different bugs), investigating them sequentially wastes time. Each investigation is independent and can happen in parallel.

**Core principle:** Dispatch one agent per independent problem domain. Let them work concurrently.

## When to Use

**Use when:**
- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from others
- No shared state between investigations

**Don't use when:**
- Failures are related (fix one might fix others)
- Need to understand full system state
- Agents would interfere with each other

## The Pattern

### 1. Identify Independent Domains

Group failures by what's broken:
- File A tests: Tool approval flow
- File B tests: Batch completion behavior
- File C tests: Abort functionality

Each domain is independent - fixing tool approval doesn't affect abort tests.

### 2. Create Focused Agent Tasks

Each agent gets:
- **Specific scope:** One test file or subsystem
- **Clear goal:** Make these tests pass
- **Constraints:** Don't change other code
- **Expected output:** Summary of what you found and fixed

### 3. Dispatch in Parallel

Use `openclaw agent spawn` to dispatch agents concurrently:

```bash
# Dispatch agents for independent problems
openclaw agent spawn --agent forge --task "Fix agent-tool-abort.test.ts failures"
openclaw agent spawn --agent forge --task "Fix batch-completion-behavior.test.ts failures"
openclaw agent spawn --agent forge --task "Fix tool-approval-race-conditions.test.ts failures"
```

Or in OpenClaw's orchestration context, dispatch via subagent mechanism.

### 4. Review and Integrate

When agents return:
- Read each summary
- Verify fixes don't conflict
- Run full test suite
- Integrate all changes

## Agent Prompt Structure

Good agent prompts are:
1. **Focused** - One clear problem domain
2. **Self-contained** - All context needed to understand the problem
3. **Specific about output** - What should the agent return?

## Common Mistakes

**BAD: Too broad:** "Fix all the tests" - agent gets lost
**GOOD: Specific:** "Fix agent-tool-abort.test.ts" - focused scope

**BAD: No context:** "Fix the race condition" - agent doesn't know where
**GOOD: Context:** Paste the error messages and test names

**BAD: No constraints:** Agent might refactor everything
**GOOD: Constraints:** "Do NOT change production code" or "Fix tests only"

**BAD: Vague output:** "Fix it" - you don't know what changed
**GOOD: Specific:** "Return summary of root cause and changes"

## When NOT to Use

**Related failures:** Fixing one might fix others - investigate together first
**Need full context:** Understanding requires seeing entire system
**Exploratory debugging:** You don't know what's broken yet
**Shared state:** Agents would interfere (editing same files, using same resources)

## Verification

After agents return:
1. **Review each summary** - Understand what changed
2. **Check for conflicts** - Did agents edit same code?
3. **Run full suite** - Verify all fixes work together
4. **Spot check** - Agents can make systematic errors
