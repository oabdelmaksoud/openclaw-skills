---
name: openclaw-agent-development
description: "This skill should be used when the user asks to 'create an agent', 'add an agent', 'write a new agent', 'configure agent SOUL.md', 'agent IDENTITY.md', 'agent workspace setup', 'agent fallback chains', 'agent model assignment', or needs guidance on OpenClaw agent structure, SOUL.md/IDENTITY.md patterns, agent configuration in openclaw.json, or agent development best practices."
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖"
      }
  }
---

# Agent Development for OpenClaw

## Overview

OpenClaw agents are autonomous AI-driven entities in a 16-agent multi-agent system. Each agent has a dedicated workspace, identity files, communication channels, and model routing with fallback chains. Understanding agent structure enables creating and configuring powerful autonomous capabilities.

**Key concepts:**
- Agents are defined in `openclaw.json` under the `agents` section
- Each agent has a workspace at `~/.openclaw/workspace/agents-workspaces/<id>/`
- Agent behavior is driven by SOUL.md (shared instructions) + IDENTITY.md (per-agent identity)
- Model routing uses primary + fallback chains across multiple providers
- Communication via file-based inboxes/outboxes in `workspace/comms/`

## Agent Workspace Structure

### Per-Agent Directory

```
~/.openclaw/workspace/agents-workspaces/<agent-id>/
├── IDENTITY.md          # Agent-specific identity and role
├── SOUL.md              # Shared behavioral instructions (symlinked or copied)
├── AGENTS.md            # Team roster awareness
├── USER.md              # User preferences and context
├── HEARTBEAT.md         # Agent health status
├── BOOTSTRAP.md         # Agent initialization instructions
└── TOOLS.md             # Available tools and capabilities
```

### Key Identity Files

**IDENTITY.md** — Defines who the agent is:
- Agent name and role
- Primary responsibilities
- Domain expertise
- Behavioral traits and style
- Idle-time standing orders

**SOUL.md** — Shared instructions read by ALL agents:
- Common protocols and standards
- Communication patterns
- Task handling procedures
- Quality standards
- File-based orchestration rules

## Agent Configuration (openclaw.json)

### Agent Entry Format

```json
{
  "agents": {
    "<agent-id>": {
      "name": "<Display Name>",
      "role": "<role-description>",
      "model": {
        "primary": "<provider/model-name>",
        "fallback": [
          "<provider1/model1>",
          "<provider2/model2>",
          "<provider3/model3>"
        ]
      }
    }
  }
}
```

### Model Assignment Best Practices

- **Critical agents** (orchestrator, debugger, security): Use strongest models (e.g., anthropic/claude-sonnet-4-6, anthropic/claude-opus-4-6)
- **High-volume agents**: Use providers with generous rate limits (e.g., MiniMax with 500 RPM)
- **No-limit agents**: Use DeepSeek for agents needing unlimited throughput
- **Fast infra agents**: Use NVIDIA NIM GPT-OSS for speed (2-4s latency)
- **All agents**: Should have Claude CLI Proxy as first fallback for zero-downtime resilience
- **Fallback chains**: 4-5 fallbacks spanning different providers

### Agent Naming Rules

- **ID**: lowercase, hyphens allowed (e.g., `solution-architect`, `predictive-analyst`)
- **Display Name**: Capitalized, memorable (e.g., `Sage`, `Oracle`, `Nova`)
- **Role**: Descriptive phrase (e.g., `Architecture, design, code review`)

## Creating a New Agent

### Step 1: Define Purpose and Identity

Determine:
- What domain does this agent cover?
- What are its primary responsibilities?
- When should it be invoked?
- What idle-time standing orders should it have?

### Step 2: Configure in openclaw.json

Add agent entry with model routing:

```json
{
  "agents": {
    "new-agent": {
      "name": "AgentName",
      "role": "Domain description",
      "model": {
        "primary": "provider/model",
        "fallback": ["claude-proxy", "deepseek/deepseek-chat", "minimax-portal/MiniMax-M2.5"]
      }
    }
  }
}
```

### Step 3: Create Workspace

```bash
mkdir -p ~/.openclaw/workspace/agents-workspaces/new-agent/
```

### Step 4: Write IDENTITY.md

```markdown
# Agent: AgentName

## Role
[Specific role description]

## Primary Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

## Domain Expertise
- [Expertise area 1]
- [Expertise area 2]

## Behavioral Traits
- [Communication style]
- [Decision-making approach]

## Idle-Time Standing Orders
When queue and backlog are empty:
1. [Standing order 1]
2. [Standing order 2]
```

### Step 5: Set Up Communications

Create inbox/outbox files:
```bash
touch ~/.openclaw/workspace/comms/inboxes/new-agent.md
touch ~/.openclaw/workspace/comms/outboxes/new-agent.md
```

### Step 6: Create Auth Profiles

Each agent needs `auth-profiles.json` for provider authentication:
- Must include Google API key for Gemini embeddings (memory search)
- Must include keys for primary and fallback providers

## SOUL.md Design Patterns

### Structure Template

```markdown
# Shared Agent Soul

## Core Protocols
[Communication and coordination rules]

## Task Handling
[How to pick up, execute, and close tickets]

## Quality Standards
[Vigil quality gate: 1-5 rating, >=3 delivers]

## File-Based Orchestration
[How to use comms/, TASKS.json, broadcast.md]

## Idle-Time Behavior
[What to do when queue is empty]
```

### Best Practices

- Write in second person ("You are...", "You will...")
- Be specific about responsibilities and boundaries
- Define clear handoff protocols between agents
- Include quality standards and output formats
- Address edge cases (rate limits, provider failures, stuck tasks)
- Keep under 10,000 characters

## Spawning Agent Tasks

To dispatch work to an agent:

```bash
openclaw agent spawn --task "Your task description here"
```

For targeted agent dispatch:
```bash
openclaw agent spawn --agent <agent-id> --task "Specific task for this agent"
```

## Validation Checklist

- [ ] Agent entry exists in `openclaw.json` with valid model routing
- [ ] Workspace directory created at `agents-workspaces/<id>/`
- [ ] IDENTITY.md written with clear role and responsibilities
- [ ] SOUL.md present (shared or symlinked)
- [ ] Auth profiles configured with required API keys
- [ ] Inbox/outbox files created in `workspace/comms/`
- [ ] Agent tested with `openclaw agent --json` (skip deprecation warnings before first `{`)

## Additional Resources

### Reference Files

- **`references/system-prompt-design.md`** — Patterns for writing effective SOUL.md/IDENTITY.md
- **`references/triggering-examples.md`** — When and how to dispatch to specific agents

### Example Files

- **`examples/agent-creation-prompt.md`** — Template for AI-assisted agent generation
- **`examples/complete-agent-examples.md`** — Full agent configurations for different roles
