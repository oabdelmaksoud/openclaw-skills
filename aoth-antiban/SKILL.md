---
name: aoth-antiban
description: "Use when managing the Claude CLI Proxy (ban protector) — start, stop, restart, status, logs, backup, test, setup, or register the proxy in OpenClaw. Triggers on: 'proxy status', 'ban protector', 'start proxy', 'stop proxy', 'proxy health', 'antiban', 'cli proxy'."
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️"
      }
  }
---

# Aoth-AntiBAN: Claude CLI Proxy Manager

## Overview

Manages the Claude CLI Proxy (ban protector) — a v4 hybrid proxy that routes text-only requests through the free Claude CLI and escalates tool/schema requests to the paid API. Features Box-Muller jitter anti-detection, circuit breaker, and LevelDB session escalation tracking.

> **Canonical source**: `~/.claude/commands/Aoth-AntiBAN.md` — this SKILL.md is a condensed mirror. For full bash examples and detailed steps, refer to the Claude Code command.

## When to Use

- User asks to start, stop, restart, or check the proxy
- User asks about ban protection or rate limit protection
- User needs to set up the proxy on a new machine
- User wants to register the proxy as an OpenClaw provider
- User asks for proxy logs or health status
- User wants to back up the proxy

## Constants

| Constant | Value |
|----------|-------|
| PROXY_DIR | `~/.openclaw/tools/claude-cli-proxy/` |
| LEGACY_DIR | `~/.gemini/antigravity/openclaw-proxy/` |
| BACKUP_DIR | `~/backups/` |
| PM2_NAME | `openclaw-claude-proxy` |
| PORT | `3000` |
| ENDPOINT | `POST http://127.0.0.1:3000/v1/chat/completions` |
| SESSION_DB | `~/.claude/proxy_escalated_sessions.db/` |
| OPENCLAW_CONFIG | `~/.openclaw/openclaw.json` |
| AUTH_JSON | `~/.openclaw/agents/*/agent/auth.json` (ALL 16 agents) |
| AUTH_PROFILES | `~/.openclaw/agents/*/agent/auth-profiles.json` (ALL 16 agents) |

## Subcommands

If the user message doesn't specify a subcommand, default to `status`.

### `setup` — Full fresh-machine setup

1. **Locate source**: Check PROXY_DIR, then LEGACY_DIR. Error if neither exists.
2. **Copy source** (if at LEGACY_DIR): `cp -R ~/.gemini/antigravity/openclaw-proxy/ ~/.openclaw/tools/claude-cli-proxy/` — keep legacy as backup.
3. **Install deps**: `cd ~/.openclaw/tools/claude-cli-proxy/ && npm install --production`. If fails, check Node.js 18+, npm, network, disk space.
4. **Clear stale LevelDB locks**: `rm -f ~/.claude/proxy_escalated_sessions.db/LOCK`
5. **Start PM2**: `cd ~/.openclaw/tools/claude-cli-proxy/ && pm2 start ecosystem.config.js && pm2 save`
6. **Enable PM2 startup** (reboot persistence): `pm2 startup` — run sudo command if prompted, then `pm2 save`.
7. **Verify**: `sleep 2 && lsof -ti:3000`
8. **Register**: Run `register` logic.
9. **Backup**: Run `backup` logic.
10. **Report**: Summary table.

### `start` — Start the proxy

1. Clear LevelDB lock: `rm -f ~/.claude/proxy_escalated_sessions.db/LOCK`
2. `cd ~/.openclaw/tools/claude-cli-proxy/ && pm2 start ecosystem.config.js && pm2 save`
3. Wait for async startup: `sleep 2`
4. Verify port 3000: `lsof -ti:3000`

### `stop` — Stop the proxy

`pm2 stop openclaw-claude-proxy`

### `restart` — Restart the proxy

1. Clear LevelDB lock.
2. `pm2 restart openclaw-claude-proxy`
3. Verify port 3000 after 2s.

### `status` — Show proxy health

Run three checks and present as table:
1. `pm2 describe openclaw-claude-proxy` — status, PID, uptime, memory, restarts
2. `lsof -ti:3000` — port listening?
3. `openclaw models list | grep claude-cli-proxy` — Auth yes?

### `logs` — Recent logs

`pm2 logs openclaw-claude-proxy --lines 50 --nostream`

### `backup` — Compressed backup

```bash
mkdir -p ~/backups/
tar -czf ~/backups/claude-cli-proxy-backup-$(date +%Y%m%d).tar.gz -C ~/.openclaw/tools/ claude-cli-proxy/
```

> **Note**: This is a quick tar backup to `~/backups/` for convenience. The system's primary backup is restic (encrypted, dedup, daily 3 AM) at `/home/openclaw/backups/`. This tar backup is separate and supplementary.

### `test` — Verify endpoint

```bash
curl -s -X POST http://127.0.0.1:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-key" \
  -d '{"model":"claude-3-5-sonnet-20241022","messages":[{"role":"user","content":"Reply with only OK"}]}' \
  --max-time 30
```

- `"choices"` in response = working
- `"nested session"` error = working (expected from Claude Code)
- Connection refused = not running

### `register` — Register in OpenClaw

1. **openclaw.json** `models.providers.claude-cli-proxy`: baseUrl `http://127.0.0.1:3000/v1`, api `openai-completions`, auth `api-key`, model `claude-3-5-sonnet-20241022` (200K ctx, 8192 max, zero cost).
2. **openclaw.json** `auth.profiles`: `"claude-cli-proxy:default": {"provider": "claude-cli-proxy", "mode": "token"}`
3. **ALL agent auth.json** (`~/.openclaw/agents/*/agent/auth.json`): `"claude-cli-proxy": {"type": "api_key", "key": "dummy-key"}` — loop through all 16 agents.
4. **ALL agent auth-profiles.json** (`~/.openclaw/agents/*/agent/auth-profiles.json`): `"claude-cli-proxy:default": {"type": "token", "provider": "claude-cli-proxy", "token": "dummy-key"}` — loop through all 16 agents.
5. Restart gateway (WARNING: kills in-flight requests): kill port 18789, `sleep 2`, `openclaw gateway start`.
6. Verify: `openclaw models list | grep claude-cli-proxy` shows Auth: yes.

> **Why all agents?** The proxy is FB1 (first fallback) for all 16 agents. If auth entries only exist for `main`, other agents will fail when falling back to the proxy.

## Routing Architecture

| Request Type | Route | Auth | Cost |
|---|---|---|---|
| **Text-only** (no tools/schemas/multimodal) | **CLI Mode** → `claude` CLI subprocess | Claude.ai subscription (OAuth session) | **$0** |
| **Tools, tool_choice, response_format, multimodal** | **Strict Mode** → Anthropic Messages API | `ANTHROPIC_API_KEY` env var (`sk-ant-oat01-...`) | Paid API |

- **CLI Mode**: Spawns `~/.local/bin/claude` with `--session-id`, `--system-prompt`, `-p`. Free via subscription.
- **Strict Mode**: Uses `@anthropic-ai/sdk` with `ANTHROPIC_API_KEY` from `ecosystem.config.js` env. The `dummy-key` in OpenClaw config is only for gateway routing — proxy internally resolves to the real key.
- **Session escalation**: Once a session uses tools, permanently escalated in LevelDB.
- **Anti-detection**: Box-Muller jitter (new: 2.5–12s, repeat: 0.5–3s), circuit breaker (8 concurrent, 50/5min).

### Anthropic OAuth Key Rotation

If the `sk-ant-oat01-...` token is rotated:
1. Update `ecosystem.config.js` → `env.ANTHROPIC_API_KEY`
2. Update all agent `auth.json` + `auth-profiles.json` (for direct API access)
3. `pm2 restart openclaw-claude-proxy --update-env`

## Error Handling

- If PM2 is not installed: `npm install -g pm2`
- If Node.js/npm is not installed: Required prerequisite — install via `nvm install --lts`
- If `npm install` fails: Check `node -v` (need 18+), `npm -v`, network (`npm ping`), disk space
- If port 3000 is in use by something else: Report the PID and process name via `lsof -ti:3000`
- If `ecosystem.config.js` is missing: The proxy source is corrupted — suggest restoring from backup
- If OpenClaw gateway won't restart: Kill stale processes on port 18789 first
- If `pm2 startup` needs sudo: Run the exact command PM2 outputs (platform-specific)

## Important Notes

- Endpoint is `POST /v1/chat/completions` (OpenAI-compatible), NOT `/v1/messages`
- `dummy-key` in OpenClaw config is intentional — proxy resolves real Anthropic key from `ANTHROPIC_API_KEY` env var
- Testing from within Claude Code always shows "nested session" error — this means the proxy IS working (CLI Mode correctly triggered)
- LevelDB at `~/.claude/proxy_escalated_sessions.db/` tracks escalated sessions
- After `npm install -g openclaw@<version>` upgrades, the `dist/apiClient.js` patch (dummy-key → env key fallback) may be overwritten — re-apply if needed
