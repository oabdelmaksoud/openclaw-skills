---
name: openclaw-md-improver
description: "Audit and improve CLAUDE.md and SOUL.md files across the OpenClaw workspace, plus openclaw.json config. Use when user asks to check, audit, update, improve, or fix CLAUDE.md files, SOUL.md agent personality files, or openclaw.json configuration. Also use when the user mentions 'config maintenance', 'project memory optimization', 'agent personality audit', or 'workspace health check'."
metadata:
  {
    "openclaw":
      {
        "emoji": "✨"
      }
  }
---

# OpenClaw MD Improver

Audit, evaluate, and improve CLAUDE.md, SOUL.md, and openclaw.json files across the OpenClaw workspace to ensure all agents have optimal project context and personality configuration.

**This skill can write to CLAUDE.md, SOUL.md, and openclaw.json files.** After presenting a quality report and getting user approval, it updates files with targeted improvements.

## Workflow

### Phase 1: Discovery

Find all configuration and instruction files in the OpenClaw workspace:

```bash
# Find CLAUDE.md files (shared agent instructions)
find ~/.openclaw/workspace -name "CLAUDE.md" 2>/dev/null | head -50

# Find SOUL.md files (per-agent personality)
find ~/.openclaw/workspace -name "SOUL.md" 2>/dev/null | head -50

# Check openclaw.json config
ls -la ~/.openclaw/openclaw.json 2>/dev/null
```

**File Types & Locations:**

| Type | Location | Purpose |
|------|----------|---------|
| Workspace root CLAUDE.md | `~/.openclaw/workspace/CLAUDE.md` | Shared instructions read by ALL 16 agents |
| Per-agent SOUL.md | `~/.openclaw/workspace/agents-workspaces/<id>/SOUL.md` | Agent personality, role, behavior |
| Per-agent IDENTITY.md | `~/.openclaw/workspace/agents-workspaces/<id>/IDENTITY.md` | Agent identity and bootstrap info |
| openclaw.json | `~/.openclaw/openclaw.json` | System config (models, providers, routing, cron) |
| Per-agent auth | `~/.openclaw/workspace/agents-workspaces/<id>/auth-profiles.json` | API keys and auth config |

**Agent Workspace IDs:**
Cooper (main), Pixel (debugger), Vault (cybersecurity), Sage (solution-architect), Oracle (predictive-analyst), Nova (nova), Mirror (metacognition), Vista (business-analyst), Forge (implementation), Vex (tester), Axon (devops), Vigil (quality-assurance), Anchor (content-specialist), Muse (creativity), Cipher (knowledge-curator), Lens (multimodal)

### Phase 2: Quality Assessment

For each file type, evaluate against appropriate criteria. See [references/quality-criteria.md](references/quality-criteria.md) for detailed rubrics.

#### CLAUDE.md Assessment Checklist

| Criterion | Weight | Check |
|-----------|--------|-------|
| Agent routing rules documented | High | Are MoE dispatch rules and agent roles clear? |
| Process workflows documented | High | Are the 23 processes referenced correctly? |
| Comms patterns documented | Medium | Is file-based message passing explained? |
| Conciseness | Medium | No verbose explanations or obvious info? |
| Currency | High | Does it reflect current 16-agent roster? |
| Actionability | High | Are instructions executable, not vague? |

#### SOUL.md Assessment Checklist

| Criterion | Weight | Check |
|-----------|--------|-------|
| Role clarity | High | Is the agent's specialization clear? |
| Personality consistency | High | Does tone match the agent's purpose? |
| Idle-time standing orders | Medium | Are standing orders defined for empty queue? |
| Model awareness | Medium | Does it reference the agent's primary model? |
| Team integration | Medium | Are communication patterns with other agents defined? |

#### openclaw.json Assessment Checklist

| Criterion | Weight | Check |
|-----------|--------|-------|
| Model routing correct | High | Do primary + fallback chains match documented roster? |
| Provider auth configured | High | Are all provider API keys/OAuth present? |
| Cron schedules correct | High | Do all 17 cron jobs have correct schedules? |
| Context windows valid | Medium | Are all contextWindow values >= 16000? |
| maxConcurrent settings | Medium | Are concurrency limits reasonable? |

**Quality Scores:**
- **A (90-100)**: Comprehensive, current, actionable
- **B (70-89)**: Good coverage, minor gaps
- **C (50-69)**: Basic info, missing key sections
- **D (30-49)**: Sparse or outdated
- **F (0-29)**: Missing or severely outdated

### Phase 3: Quality Report Output

**ALWAYS output the quality report BEFORE making any updates.**

Format:

```
## OpenClaw Configuration Quality Report

### Summary
- CLAUDE.md files found: X
- SOUL.md files found: X
- openclaw.json status: [present/missing]
- Average score: X/100
- Files needing update: X

### File-by-File Assessment

#### 1. ~/.openclaw/workspace/CLAUDE.md (Shared Root)
**Score: XX/100 (Grade: X)**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Agent routing rules | X/20 | ... |
| Process workflows | X/20 | ... |
| Comms patterns | X/15 | ... |
| Conciseness | X/15 | ... |
| Currency | X/15 | ... |
| Actionability | X/15 | ... |

**Issues:**
- [List specific problems]

**Recommended additions:**
- [List what should be added]

#### 2. ~/.openclaw/workspace/agents-workspaces/main/SOUL.md (Cooper)
...

#### 3. ~/.openclaw/openclaw.json (System Config)
...
```

### Phase 4: Targeted Updates

After outputting the quality report, ask user for confirmation before updating.

**Update Guidelines (Critical):**

1. **Propose targeted additions only** - Focus on genuinely useful info:
   - Agent routing rules or dispatch patterns discovered during analysis
   - Gotchas or non-obvious patterns found in configuration
   - Agent relationships that weren't clear
   - Process workflows that work
   - Configuration quirks

2. **Keep it minimal** - Avoid:
   - Restating what's obvious from the config
   - Generic best practices already covered
   - One-off fixes unlikely to recur
   - Verbose explanations when a one-liner suffices

3. **Show diffs** - For each change, show:
   - Which file to update
   - The specific addition (as a diff or quoted block)
   - Brief explanation of why this helps future sessions

**Diff Format:**

```markdown
### Update: ~/.openclaw/workspace/CLAUDE.md

**Why:** Agent routing rules were missing, causing confusion about dispatch.

```diff
+ ## Agent Routing
+
+ | Tag | Agent | When |
+ |-----|-------|------|
+ | security | Vault | Threat analysis, auth review |
+ | debug | Pixel | Root cause analysis |
+ | research | Nova | R&D tasks only |
```
```

### Phase 5: Apply Updates

After user approval, apply changes using the Edit tool. Preserve existing content structure.

## Templates

See [references/templates.md](references/templates.md) for CLAUDE.md and SOUL.md templates.

## Common Issues to Flag

1. **Stale agent roster**: CLAUDE.md references agents that have been removed or renamed
2. **Missing SOUL.md**: Agent workspace exists but SOUL.md is blank or missing
3. **Model mismatch**: openclaw.json model assignments don't match CLAUDE.md roster table
4. **Broken fallback chains**: Fallback models reference non-existent providers
5. **Cron schedule conflicts**: Multiple crons targeting same agent at same time
6. **Missing auth profiles**: Agent auth-profiles.json missing Google API key for Gemini embeddings
7. **Context window too small**: Models with contextWindow < 16000 will be blocked by gateway

## User Tips to Share

When presenting recommendations, remind users:

- **Keep CLAUDE.md concise**: It's read by ALL 16 agents — every line costs context across all sessions
- **SOUL.md is per-agent**: Put agent-specific personality and behavior here, not in shared CLAUDE.md
- **openclaw.json is the source of truth**: Model routing, cron jobs, and provider config all live here
- **Test after changes**: Run `openclaw doctor` to verify config health
- **Backup first**: Config is backed up nightly via restic, but manual backup before big changes is wise

## What Makes Great OpenClaw Configuration

**CLAUDE.md principles:**
- Concise and shared — only instructions ALL agents need
- Agent routing table current with all 16 agents
- Process references accurate (23 processes, L1-L4 maturity)
- Comms patterns clear (file-based inboxes/outboxes)

**SOUL.md principles:**
- Clear role and specialization
- Personality that matches the agent's purpose
- Standing orders for idle time
- Communication style defined

**openclaw.json principles:**
- All 16 agents with correct primary + fallback chains
- Provider auth configured and verified
- Cron schedules non-overlapping where possible
- Gateway rate limits appropriate
