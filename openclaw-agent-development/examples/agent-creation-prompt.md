# AI-Assisted Agent Generation Template for OpenClaw

Use this template to generate new OpenClaw agents.

## Usage Pattern

### Step 1: Describe Your Agent Need

Think about:
- What domain should the agent cover?
- What are its primary responsibilities?
- Should it be proactive or reactive?
- Which existing agents does it complement?

### Step 2: Design Agent Identity

Create the agent configuration:

```json
{
  "identifier": "agent-id",
  "displayName": "AgentName",
  "role": "Domain description",
  "primaryModel": "provider/model-name",
  "fallbackChain": ["claude-proxy", "deepseek/deepseek-chat", "minimax-portal/MiniMax-M2.5"],
  "responsibilities": [
    "Responsibility 1",
    "Responsibility 2"
  ]
}
```

### Step 3: Create IDENTITY.md

Write the agent's identity file at `~/.openclaw/workspace/agents-workspaces/<id>/IDENTITY.md`:

```markdown
# Agent: <DisplayName>

## Role
<Specific role description>

## Primary Responsibilities
1. <Responsibility 1>
2. <Responsibility 2>
3. <Responsibility 3>

## Domain Expertise
- <Expertise 1>
- <Expertise 2>

## Behavioral Traits
- <Communication style>
- <Decision-making approach>

## Idle-Time Standing Orders
When queue and backlog are empty:
1. <Standing order 1>
2. <Standing order 2>
```

### Step 4: Add to openclaw.json

```json
{
  "agents": {
    "<id>": {
      "name": "<DisplayName>",
      "role": "<role>",
      "model": {
        "primary": "<provider/model>",
        "fallback": [
          "claude-proxy",
          "<fallback-1>",
          "<fallback-2>",
          "<fallback-3>",
          "<fallback-4>"
        ]
      }
    }
  }
}
```

### Step 5: Set Up Communications and Auth

```bash
# Create workspace
mkdir -p ~/.openclaw/workspace/agents-workspaces/<id>/

# Create comms files
touch ~/.openclaw/workspace/comms/inboxes/<id>.md
touch ~/.openclaw/workspace/comms/outboxes/<id>.md

# Set up auth (copy from existing agent and modify)
cp ~/.openclaw/workspace/agents-workspaces/main/auth-profiles.json ~/.openclaw/workspace/agents-workspaces/<id>/auth-profiles.json
chmod 600 ~/.openclaw/workspace/agents-workspaces/<id>/auth-profiles.json
```

## Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Critical reasoning | anthropic/claude-opus-4-6 | Most capable |
| General purpose | anthropic/claude-sonnet-4-6 | Balanced |
| High volume | minimax-portal/MiniMax-M2.5 | 500 RPM |
| Unlimited | deepseek/deepseek-chat | No hard limits |
| Fast infra | nvidia-nim/openai/gpt-oss-120b | 2-4s latency |
| Multimodal | google/gemini-3.1-pro | Vision + search |

## Validation Checklist

- [ ] Agent entry in openclaw.json
- [ ] IDENTITY.md with clear role and responsibilities
- [ ] Workspace directory created
- [ ] Auth profiles with required API keys
- [ ] Inbox/outbox files created
- [ ] Agent tested with `openclaw agent --json`
