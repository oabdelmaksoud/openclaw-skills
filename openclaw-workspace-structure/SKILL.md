---
name: openclaw-workspace-structure
description: "This skill should be used when the user asks to 'understand workspace structure', 'organize workspace', 'set up OpenClaw workspace', 'where do files go', 'workspace layout', 'agent workspace paths', or needs guidance on OpenClaw directory layout, file organization, component locations, or workspace architecture best practices."
metadata:
  {
    "openclaw":
      {
        "emoji": "📁"
      }
  }
---

# OpenClaw Workspace Structure

## Overview

OpenClaw follows a standardized directory structure rooted at `~/.openclaw/` with a central workspace for all agent collaboration, communication, and task management. Understanding this structure enables effective navigation and maintenance of the multi-agent system.

**Key concepts:**
- Central config at `~/.openclaw/openclaw.json`
- Workspace at `~/.openclaw/workspace/` for all agent collaboration
- Per-agent workspaces under `workspace/agents-workspaces/<id>/`
- File-based orchestration (no coordination code)
- Same structure on server (`/home/openclaw/`) via Tailscale

## Top-Level Directory Structure

```
~/.openclaw/
├── openclaw.json                    # Central configuration
├── workspace/                       # All agent collaboration
│   ├── CLAUDE.md                   # Shared instructions (read by ALL agents)
│   ├── TASKS.json                  # Task tracking (full schema with RACI)
│   ├── SPRINT_CURRENT.json         # Active global sprint
│   ├── SHARED_KNOWLEDGE.json       # Semantic memory
│   ├── IMPROVEMENT_BACKLOG.json    # Continuous improvement items (>=5 required)
│   ├── agents-workspaces/          # Per-agent directories
│   ├── comms/                      # Communication channels
│   ├── processes/                  # Process definitions
│   ├── standards/                  # Quality and coding standards
│   ├── meetings/                   # Meeting records
│   ├── projects/                   # Project files
│   ├── sprints/                    # Sprint archives and per-project sprints
│   ├── teams/                      # Team configurations (e.g., R&D)
│   ├── tools/                      # Shared tools and utilities
│   └── rca/                        # Root Cause Analysis reports
├── skills/                          # OpenClaw skills (SKILL.md files)
├── memory/                          # LanceDB memory database
│   └── lancedb/                    # Vector embeddings
└── models.json                      # Model registry
```

## Agent Workspaces

### Per-Agent Directory

```
workspace/agents-workspaces/<agent-id>/
├── IDENTITY.md          # Agent-specific identity and role
├── SOUL.md              # Shared behavioral instructions
├── AGENTS.md            # Team roster awareness
├── USER.md              # User preferences
├── HEARTBEAT.md         # Health status
├── BOOTSTRAP.md         # Initialization instructions
├── TOOLS.md             # Available tools
└── auth-profiles.json   # Provider authentication (chmod 600)
```

### Agent ID to Workspace Mapping

| Agent | ID | Workspace |
|-------|----|-----------|
| Cooper | main | agents-workspaces/main/ |
| Pixel | debugger | agents-workspaces/debugger/ |
| Vault | cybersecurity | agents-workspaces/cybersecurity/ |
| Sage | solution-architect | agents-workspaces/solution-architect/ |
| Oracle | predictive-analyst | agents-workspaces/predictive-analyst/ |
| Nova | nova | agents-workspaces/nova/ |
| Mirror | metacognition | agents-workspaces/metacognition/ |
| Vista | business-analyst | agents-workspaces/business-analyst/ |
| Forge | implementation | agents-workspaces/implementation/ |
| Vex | tester | agents-workspaces/tester/ |
| Axon | devops | agents-workspaces/devops/ |
| Vigil | quality-assurance | agents-workspaces/quality-assurance/ |
| Anchor | content-specialist | agents-workspaces/content-specialist/ |
| Muse | creativity | agents-workspaces/creativity/ |
| Cipher | knowledge-curator | agents-workspaces/knowledge-curator/ |
| Lens | multimodal | agents-workspaces/multimodal/ |

## Communication Structure

```
workspace/comms/
├── inboxes/
│   ├── main.md              # Cooper's inbox
│   ├── debugger.md          # Pixel's inbox
│   ├── cybersecurity.md     # Vault's inbox
│   └── ...                  # One per agent
├── outboxes/
│   ├── main.md              # Cooper's outbox
│   └── ...                  # One per agent
└── broadcast.md             # System-wide announcements
```

**Communication protocol:**
- Agents write to recipient's inbox file
- Agents read from their own inbox
- broadcast.md for system-wide messages
- Watchers notified via their comms/inboxes

## Process and Standards Structure

```
workspace/processes/
├── PROCESSES.json           # All process definitions (23 processes)
└── CHANGELOG.md             # Process change history

workspace/standards/
├── coding.md                # Coding standards
├── quality.md               # Quality standards
├── documentation.md         # Documentation standards
└── research.md              # Research standards
```

## Project Structure

```
workspace/projects/
├── <project-id>/
│   ├── README.md
│   └── ...

workspace/sprints/
├── projects/
│   ├── PRJ-001_CURRENT.json
│   ├── PRJ-002_CURRENT.json
│   └── ...
└── archived/                # Completed sprints
```

## Team Structure (R&D)

```
workspace/teams/rnd/
├── TEAM.md                  # Team charter and membership
├── SPRINT_LOG.md            # Sprint history
├── DISCOVERIES.json         # Research findings
├── FRONTIER.md              # Exploration domains
├── METHODS.json             # Research methodologies
└── sprints/                 # Sprint artifacts
```

**R&D Team (Horizon Squad):** Nova (lead, permanent) + 5 rotating members

## Memory Structure

```
~/.openclaw/memory/
├── lancedb/                 # Vector embeddings (Gemini embeddings)
├── MEMORY.md                # Project memory documentation
└── gotchas.md               # Known issues and solutions

workspace/
├── SHARED_KNOWLEDGE.json    # Semantic memory
├── rca/                     # Root Cause Analysis (episodic memory)
└── processes/PROCESSES.json # Procedural memory
```

**Three memory types:**
1. **Episodic**: FAILURES.md, RCA reports
2. **Semantic**: SHARED_KNOWLEDGE.json
3. **Procedural**: PROCESSES.json

## Skills Structure

```
~/.openclaw/skills/
├── skill-name/
│   ├── SKILL.md             # Required: skill definition
│   ├── references/          # Reference documentation
│   ├── examples/            # Working examples
│   └── scripts/             # Utility scripts
└── another-skill/
    └── SKILL.md
```

## Key File Paths Quick Reference

| File | Path | Purpose |
|------|------|---------|
| Config | `~/.openclaw/openclaw.json` | Central configuration |
| Shared Instructions | `workspace/CLAUDE.md` | Read by ALL agents |
| Tasks | `workspace/TASKS.json` | Task tracking |
| Sprint | `workspace/SPRINT_CURRENT.json` | Active sprint |
| Processes | `workspace/processes/PROCESSES.json` | Process definitions |
| Standards | `workspace/standards/*.md` | Quality standards |
| Agent Identity | `agents-workspaces/<id>/IDENTITY.md` | Per-agent role |
| Agent Auth | `agents-workspaces/<id>/auth-profiles.json` | API keys |
| Inboxes | `comms/inboxes/<id>.md` | Agent message inbox |
| Memory DB | `~/.openclaw/memory/lancedb/` | Vector embeddings |
| Gateway Logs | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` | Runtime logs |
| Backup | `/home/openclaw/backups/` | restic encrypted backup |

## File Organization Best Practices

1. **Never hardcode absolute paths** — use `~/.openclaw/` prefix
2. **Agent data stays in agent workspace** — do not scatter agent files
3. **Shared data goes in workspace root** — TASKS.json, SHARED_KNOWLEDGE.json
4. **Secure sensitive files** — `chmod 600` on auth-profiles.json, openclaw.json
5. **Skills are self-contained** — each skill in its own directory with SKILL.md
6. **Server mirrors local** — same structure at `/home/openclaw/` on the droplet

## Additional Resources

### Reference Files
- **`references/component-patterns.md`** — Patterns for organizing workspace components
- **`references/manifest-reference.md`** — openclaw.json schema reference

### Example Files
- **`examples/minimal-workspace.md`** — Minimal workspace setup
- **`examples/standard-workspace.md`** — Standard 16-agent workspace
- **`examples/advanced-workspace.md`** — Full workspace with R&D team and sprints
