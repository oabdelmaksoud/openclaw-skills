---
name: openclaw-settings
description: "This skill should be used when the user asks about 'OpenClaw settings', 'configure openclaw.json', 'skill configuration', 'per-project settings', 'agent configuration', 'model routing', 'provider settings', 'skills.entries config', or wants to make OpenClaw behavior configurable through openclaw.json."
metadata:
  {
    "openclaw":
      {
        "emoji": "⚙️"
      }
  }
---

# OpenClaw Settings Configuration

## Overview

OpenClaw stores all configuration in `~/.openclaw/openclaw.json`. This central configuration file controls agent routing, model assignments, provider authentication, skill entries, cron jobs, gateway settings, and system-wide defaults.

**Key characteristics:**
- File location: `~/.openclaw/openclaw.json`
- Structure: JSON with nested sections for each subsystem
- Purpose: Central configuration for the entire 16-agent system
- Lifecycle: Persists across updates (npm install does not overwrite `~/.openclaw/` data)

## Configuration Structure

### Top-Level Sections

```json
{
  "agents": { ... },
  "agents.defaults": { ... },
  "models": { ... },
  "providers": { ... },
  "gateway": { ... },
  "crons": { ... },
  "skills": { ... },
  "plugins": { ... },
  "subagents": { ... }
}
```

## Agent Configuration

### Agent Entry

```json
{
  "agents": {
    "<agent-id>": {
      "name": "DisplayName",
      "role": "Role description",
      "model": {
        "primary": "provider/model-name",
        "fallback": [
          "claude-proxy",
          "deepseek/deepseek-chat",
          "minimax-portal/MiniMax-M2.5",
          "nvidia-nim/openai/gpt-oss-120b",
          "zhipu-ai/glm-4.7"
        ]
      }
    }
  }
}
```

### Agent Defaults

```json
{
  "agents.defaults": {
    "maxConcurrent": 5,
    "model": {
      "primary": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

**Important:** Per-agent `maxConcurrent` is NOT supported in the schema. Only `agents.defaults.maxConcurrent` is valid.

## Skill Configuration

### skills.entries

Configure skill-specific settings:

```json
{
  "skills": {
    "entries": {
      "my-skill-name": {
        "enabled": true,
        "setting1": "value1",
        "setting2": 42
      }
    }
  }
}
```

Skills read their configuration from this section to customize behavior per-installation.

### Adding a Skill Entry

1. Identify the skill name (from SKILL.md frontmatter)
2. Add entry under `skills.entries` in openclaw.json
3. Define any custom settings the skill needs
4. Restart OpenClaw gateway for changes to take effect

## Provider Configuration

### Provider Entry

```json
{
  "providers": {
    "anthropic": {
      "type": "anthropic",
      "auth": "oauth"
    },
    "deepseek": {
      "type": "openai-compatible",
      "baseUrl": "https://api.deepseek.com/v1",
      "auth": "api-key"
    },
    "nvidia-nim": {
      "type": "openai-compatible",
      "baseUrl": "https://integrate.api.nvidia.com/v1",
      "auth": "api-key"
    }
  }
}
```

### Auth Profiles (Per-Agent)

Each agent has `auth-profiles.json` at:
```
~/.openclaw/workspace/agents-workspaces/<agent-id>/auth-profiles.json
```

**Must include:**
- API keys for primary and fallback providers
- Google API key (`google:default`) for Gemini embeddings (memory search)

**Critical gotcha:** DeepSeek API key goes in `auth-profiles.json`, NOT in openclaw.json (gateway rejects inline keys in auth.profiles section).

## Gateway Configuration

```json
{
  "gateway": {
    "port": 18789,
    "auth": {
      "rateLimit": {
        "attempts": 10,
        "window": "1m",
        "lockout": "5m"
      }
    }
  }
}
```

**Note:** Gateway has a hard 16000 minimum contextWindow check. Models with < 16K context are blocked.

## Cron Configuration

```json
{
  "crons": {
    "heartbeat-monitor": {
      "schedule": "*/5 * * * *",
      "agent": "quality-assurance",
      "task": "Run heartbeat check",
      "model": "nvidia-nim/openai/gpt-oss-120b"
    }
  }
}
```

**Rules:**
- All crons use `--no-deliver --session isolated`
- Use model overrides for fast/unlimited models
- Never exceed 1 concurrent dispatch per cron run

## Memory Plugin Configuration

```json
{
  "plugins": {
    "slots": {
      "memory": "memory-lancedb"
    }
  }
}
```

**Only one memory plugin can be active at a time.** Default is `memory-core`. Set to `memory-lancedb` for LanceDB-backed memory with Gemini embeddings.

## Common Configuration Patterns

### Adding a New Model

```json
{
  "models": {
    "new-provider/model-name": {
      "contextWindow": 32000,
      "maxOutput": 8192,
      "pricing": { "input": 0.001, "output": 0.003 }
    }
  }
}
```

### Adjusting Concurrency

```json
{
  "agents.defaults": {
    "maxConcurrent": 5
  },
  "subagents": {
    "maxConcurrent": 5
  }
}
```

### Enabling/Disabling Skills

```json
{
  "skills": {
    "entries": {
      "my-skill": { "enabled": false }
    }
  }
}
```

## Validation and Safety

### After Configuration Changes

1. Verify gateway is running: `curl http://127.0.0.1:18789/`
2. Run `openclaw doctor` to validate configuration
3. Test agent connectivity: `openclaw agent --json` (skip to first `{`)
4. Check gateway logs: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`

### Security Best Practices

- Secure sensitive files: `chmod 600 openclaw.json`
- Never commit API keys to git
- Use auth-profiles.json for per-agent secrets
- Store DeepSeek cooldown fields (`disabledUntil`, `disabledReason`) in auth-profiles.json

## Common Gotchas

- API keys ARE required in models.json for gateway auth. Do NOT remove apiKey fields.
- `openclaw agent --json` has deprecation warnings before JSON — skip to first `{`
- Per-agent `maxConcurrent` NOT supported — only `agents.defaults.maxConcurrent`
- Gateway 16K minimum contextWindow check blocks models with < 16K
- npm install overwrites dist files but preserves `~/.openclaw/` data

## Additional Resources

### Reference Files
- **`references/parsing-techniques.md`** — Techniques for reading and modifying openclaw.json
- **`references/real-world-examples.md`** — Production configuration examples

### Example Files
- **`examples/example-settings.md`** — Template openclaw.json with annotations
