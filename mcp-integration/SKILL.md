---
name: mcp-integration
description: "This skill should be used when the user asks to 'add MCP server', 'integrate MCP', 'configure MCP', 'use .mcp.json', 'set up Model Context Protocol', 'connect external service via MCP', or discusses MCP server types (SSE, stdio, HTTP, WebSocket). Provides comprehensive guidance for integrating Model Context Protocol servers into OpenClaw for external tool and service integration."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔗"
      }
  }
---

# MCP Integration for OpenClaw

## Overview

Model Context Protocol (MCP) enables OpenClaw agents to integrate with external services and APIs by providing structured tool access. Use MCP integration to expose external service capabilities as tools within OpenClaw agent sessions.

**Key capabilities:**
- Connect to external services (databases, APIs, file systems)
- Provide 10+ related tools from a single service
- Handle OAuth and complex authentication flows
- Configure MCP servers in `openclaw.json` or `.mcp.json`

## MCP Server Configuration

### Method 1: openclaw.json (Recommended)

Add MCP servers to `openclaw.json` under the `mcpServers` section:

```json
{
  "mcpServers": {
    "database-tools": {
      "command": "node",
      "args": ["~/.openclaw/servers/db-server.js", "--config", "config.json"],
      "env": {
        "DB_URL": "${DB_URL}"
      }
    }
  }
}
```

### Method 2: Dedicated .mcp.json

Create `.mcp.json` at workspace root (`~/.openclaw/.mcp.json`):

```json
{
  "database-tools": {
    "command": "~/.openclaw/servers/db-server",
    "args": ["--config", "~/.openclaw/config.json"],
    "env": {
      "DB_URL": "${DB_URL}"
    }
  }
}
```

## MCP Server Types

### stdio (Local Process)

Execute local MCP servers as child processes:

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
    "env": {
      "LOG_LEVEL": "debug"
    }
  }
}
```

**Use cases:** File system access, local databases, custom MCP servers, NPM-packaged servers

### SSE (Server-Sent Events)

Connect to hosted MCP servers with OAuth support:

```json
{
  "asana": {
    "type": "sse",
    "url": "https://mcp.asana.com/sse"
  }
}
```

**Use cases:** Official hosted MCP servers, cloud services, OAuth-based authentication

### HTTP (REST API)

Connect to RESTful MCP servers:

```json
{
  "api-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}"
    }
  }
}
```

### WebSocket (Real-time)

Connect to WebSocket MCP servers:

```json
{
  "realtime-service": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": {
      "Authorization": "Bearer ${TOKEN}"
    }
  }
}
```

## Environment Variable Expansion

All MCP configurations support environment variable substitution:

```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}",
    "DATABASE_URL": "${DB_URL}"
  }
}
```

**Best practice:** Document all required environment variables. Store sensitive values in auth-profiles.json files per agent, not in plain text.

## MCP Tool Naming

When MCP servers provide tools, they follow the naming pattern:

**Format:** `mcp__<server-name>__<tool-name>`

**Example:**
- Server: `asana`
- Tool: `create_task`
- **Full name:** `mcp__asana__create_task`

## Integration with OpenClaw Agents

### Agent-Specific MCP Access

Different agents can be configured to use different MCP servers based on their role:

| Agent | MCP Servers | Purpose |
|-------|-------------|---------|
| Forge (implementation) | filesystem, github | Code access and PR management |
| Vista (business-analyst) | asana, jira | Task and project management |
| Axon (devops) | docker, kubernetes | Infrastructure management |
| Lens (multimodal) | web-search, image-tools | Multimodal capabilities |

### Multi-Agent MCP Patterns

```json
{
  "mcpServers": {
    "github": {
      "type": "sse",
      "url": "https://mcp.github.com/sse"
    },
    "jira": {
      "type": "sse",
      "url": "https://mcp.jira.com/sse"
    }
  }
}
```

## Authentication Patterns

### OAuth (SSE/HTTP)
OAuth flows handled automatically. User authenticates on first use.

### Token-Based (Headers)
```json
{
  "type": "http",
  "url": "https://api.example.com",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

### Environment Variables (stdio)
```json
{
  "command": "python",
  "args": ["-m", "my_mcp_server"],
  "env": {
    "DATABASE_URL": "${DB_URL}",
    "API_KEY": "${API_KEY}"
  }
}
```

## Security Best Practices

- Always use HTTPS/WSS (never HTTP/WS for production)
- Use environment variables for tokens, never hardcode
- Store API keys in agent `auth-profiles.json` files
- Restrict MCP tool access per agent based on role (principle of least privilege)
- Document required environment variables in workspace README

## Error Handling

- **Connection failures**: Check server URL, network, and configuration
- **Tool call errors**: Validate inputs, check rate limits
- **Configuration errors**: Validate JSON syntax, test connectivity
- **Auth failures**: Clear cached tokens, re-authenticate, verify env vars

## Quick Reference

### MCP Server Types

| Type | Transport | Best For | Auth |
|------|-----------|----------|------|
| stdio | Process | Local tools, custom servers | Env vars |
| SSE | HTTP | Hosted services, cloud APIs | OAuth |
| HTTP | REST | API backends, token auth | Tokens |
| ws | WebSocket | Real-time, streaming | Tokens |

### Configuration Checklist

- [ ] Server type specified (stdio/SSE/HTTP/ws)
- [ ] Type-specific fields complete (command or url)
- [ ] Authentication configured
- [ ] Environment variables documented
- [ ] HTTPS/WSS used (not HTTP/WS)
- [ ] `~/.openclaw/` paths used (no hardcoded absolute paths)

## Additional Resources

### Reference Files
- **`references/server-types.md`** — Deep dive on each server type
- **`references/authentication.md`** — Authentication patterns and OAuth
- **`references/tool-usage.md`** — Using MCP tools in commands and agents
