---
name: openclaw-automation-recommender
description: "Analyze a codebase or workspace and recommend OpenClaw automations (cron jobs, skills, agent routing, processes, MCP servers, workspace structure). Use when user asks for automation recommendations, wants to optimize their OpenClaw setup, mentions improving OpenClaw workflows, asks how to best configure OpenClaw for a project, or wants to know what OpenClaw features they should use."
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖"
      }
  }
---

# OpenClaw Automation Recommender

Analyze workspace patterns to recommend tailored OpenClaw automations across all extensibility options.

**This skill is read-only.** It analyzes the workspace and outputs recommendations. It does NOT create or modify any files. Users implement the recommendations themselves or ask an agent separately to help build them.

## Output Guidelines

- **Recommend 1-2 of each type**: Don't overwhelm — surface the top 1-2 most valuable automations per category
- **If user asks for a specific type**: Focus only on that type and provide more options (3-5 recommendations)
- **Go beyond the reference lists**: The reference files contain common patterns, but use web search to find recommendations specific to the workspace's tools, frameworks, and libraries
- **Tell users they can ask for more**: End by noting they can request more recommendations for any specific category

## Automation Types Overview

| Type | Best For |
|------|----------|
| **Cron Jobs** | Scheduled recurring tasks (defined via `openclaw cron`) |
| **Skills** | Packaged expertise, workflows, and repeatable tasks (in `~/.openclaw/skills/`) |
| **Agent Routing** | Dispatching tasks to the right specialist from the 16-agent roster |
| **Processes** | Formalized workflows with maturity levels (L1-L4) |
| **MCP Servers** | External tool integrations (databases, APIs, browsers, docs) |
| **Workspace Structure** | File-based orchestration organization |

## Workflow

### Phase 1: Workspace Analysis

Gather project context:

```bash
# Check OpenClaw configuration
ls -la ~/.openclaw/openclaw.json
cat ~/.openclaw/openclaw.json 2>/dev/null | head -100

# Check existing cron jobs
openclaw cron list 2>/dev/null

# Check existing skills
ls -la ~/.openclaw/skills/ 2>/dev/null

# Check workspace structure
ls -la ~/.openclaw/workspace/ 2>/dev/null

# Check agent workspaces
ls ~/.openclaw/workspace/agents-workspaces/ 2>/dev/null

# Check processes
cat ~/.openclaw/workspace/processes/PROCESSES.json 2>/dev/null | head -50

# Check project files
ls ~/.openclaw/workspace/projects/ 2>/dev/null

# Analyze project structure if applicable
ls -la src/ app/ lib/ tests/ components/ pages/ api/ 2>/dev/null
```

**Key Indicators to Capture:**

| Category | What to Look For | Informs Recommendations For |
|----------|------------------|----------------------------|
| Existing cron jobs | Schedule gaps, overlaps | Cron jobs |
| Agent utilization | Which agents are idle/busy | Agent routing |
| Project complexity | Number of projects, tasks | Processes, workspace structure |
| Language/Framework | package.json, pyproject.toml | Skills, MCP servers |
| External APIs | Stripe, AWS, databases | MCP servers |
| Team patterns | Comms volume, ticket velocity | Processes, cron jobs |
| Quality gates | Vigil scores, RCA frequency | Skills, processes |

### Phase 2: Generate Recommendations

Based on analysis, generate recommendations across all categories:

#### A. Cron Job Recommendations

Cron jobs are scheduled via `openclaw cron` and run with `--no-deliver --session isolated`.

| Workspace Signal | Recommended Cron Job |
|-----------------|---------------------|
| No daily synthesis | **daily-synthesis** — Cipher summarizes daily activity |
| No health monitoring | **heartbeat-monitor** — Vigil checks agent health every 5m |
| No memory maintenance | **memory-reindex** — Cipher reindexes LanceDB every 6h |
| Stale processes | **self-reflection** — Vigil audits process maturity every 3h |
| No risk tracking | **weekly-risk-scan** — Sage reviews system risks weekly |
| R&D team idle | **rnd-continuous** — Nova runs frontier research every 4h |
| No reports | **daily-report** — Cooper generates daily status at 9 AM |

**Cron job best practices:**
- Always use `--no-deliver` (critical — even best-effort with no chat window records error)
- Always use `--session isolated` (sandboxed, fresh context per run)
- Use `--model` override for specific providers (e.g., `--model deepseek/deepseek-chat` for unlimited)
- Never dispatch Anthropic-primary agents concurrently (shared OAuth rate limits)
- Max 1 dispatch per cron run (prevents race conditions on tickets.json)

#### B. Skills Recommendations

See [references/skills-reference.md](references/skills-reference.md) for details.

Create skills in `~/.openclaw/skills/<name>/SKILL.md`:

| Workspace Signal | Skill to Create |
|-----------------|-----------------|
| API routes in project | **api-doc** (with OpenAPI template) |
| Database project | **create-migration** (with validation script) |
| Test suite exists | **gen-test** (with example tests) |
| Component library | **new-component** (with templates) |
| Frequent deployments | **deploy-checklist** (with prereq script) |
| Code style inconsistency | **project-conventions** (agent-invoked) |
| New contributor onboarding | **setup-dev** (with prereq script) |
| RCA reports needed | **rca-template** (with RCA workflow) |

#### C. Agent Routing Recommendations

OpenClaw has a 16-agent roster with MoE (Mixture of Experts) tag-based dispatch:

| Workspace Signal | Recommended Routing |
|-----------------|---------------------|
| Security-sensitive code | Route to **Vault** (cybersecurity) |
| Complex debugging | Route to **Pixel** (root cause analysis, uses Opus) |
| Architecture decisions | Route to **Sage** (solution architect) |
| Frontend/UI work | Route to **Muse** (creativity) + **Forge** (implementation) |
| Research tasks | Route to **Nova** (R&D lead — never assign regular tickets) |
| Content/documentation | Route to **Anchor** (content specialist) |
| Infrastructure/deployment | Route to **Axon** (DevOps) |
| Quality assurance | Route to **Vex** (adversarial testing) + **Vigil** (quality gate) |
| Business analysis | Route to **Vista** (business analyst) |
| Predictions/foresight | Route to **Oracle** (predictive analyst) |

**Agent routing best practices:**
- Cooper (main) orchestrates — routes, delegates, synthesizes
- Nova is R&D-only — never assign regular tickets
- Pixel uses Opus (expensive) — reserve for complex debugging
- MoE routing is tag-based, not availability-based
- Each agent has idle-time standing orders when queue + backlog empty

#### D. Process Recommendations

Processes are formalized workflows in `~/.openclaw/workspace/processes/PROCESSES.json` with maturity levels:

| Workspace Signal | Recommended Process |
|-----------------|---------------------|
| No incident response | **Incident Response** (L2+) — structured triage and RCA |
| No code review flow | **Code Review** (L2+) — multi-agent review with quality gates |
| No deployment pipeline | **Deployment** (L3+) — staged rollout with health checks |
| No sprint workflow | **Sprint Planning** (L3+) — per-project sprint management |
| No knowledge capture | **Knowledge Synthesis** (L2+) — Cipher captures learnings |
| No onboarding | **Agent Onboarding** (L1) — bootstrap new agents |

**Process maturity levels:**
- L1: Ad hoc — just documented
- L2: Documented — has steps and roles
- L3: Practiced — used 3+ times with evidence
- L4: Optimized — measured and improved

#### E. MCP Server Recommendations

See [references/mcp-servers.md](references/mcp-servers.md) for detailed patterns.

| Workspace Signal | Recommended MCP Server |
|-----------------|------------------------|
| Uses popular libraries | **context7** — Live documentation lookup |
| Frontend with UI testing | **Playwright** — Browser automation/testing |
| GitHub repository | **GitHub MCP** — Issues, PRs, actions |
| PostgreSQL/MySQL database | **Database MCP** — Query and schema tools |
| Uses Supabase | **Supabase MCP** — Direct database operations |
| AWS infrastructure | **AWS MCP** — Cloud resource management |
| Memory/context persistence | **Memory MCP** — Cross-session memory |
| Docker containers | **Docker MCP** — Container management |

#### F. Workspace Structure Recommendations

| Workspace Signal | Recommended Structure |
|-----------------|----------------------|
| No comms organization | Set up `workspace/comms/inboxes/` and `outboxes/` per agent |
| No project organization | Create `workspace/projects/<project-id>/` structure |
| No sprint tracking | Add `workspace/sprints/projects/<project-id>_CURRENT.json` |
| No RCA archive | Create `workspace/rca/` for root cause analyses |
| No standards docs | Add `workspace/standards/` (coding, quality, documentation, research) |
| No team structure | Define teams in `workspace/teams/` (like R&D Horizon Squad) |

### Phase 3: Output Recommendations Report

Format recommendations clearly. **Only include 1-2 recommendations per category** — the most valuable ones. Skip categories that aren't relevant.

```markdown
## OpenClaw Automation Recommendations

I've analyzed your workspace and identified the top automations for each category.

### Workspace Profile
- **Agents Active**: [count]/16
- **Cron Jobs**: [count]/17
- **Skills**: [count]
- **Processes**: [count]/23
- **Projects**: [count]

---

### ⏰ Cron Jobs

#### [cron name]
**Why**: [specific reason based on detected gaps]
**Setup**: `openclaw cron add --name "[name]" --schedule "[cron]" --agent [agent-id] --no-deliver --session isolated`
**Model Override**: `--model [provider/model]`

---

### 🎯 Skills

#### [skill name]
**Why**: [specific reason]
**Create**: `~/.openclaw/skills/[name]/SKILL.md`

---

### 🧠 Agent Routing

#### [routing recommendation]
**Why**: [specific reason based on workspace patterns]
**Tag**: [dispatch tag]
**Agent**: [agent name] ([agent id])

---

### 📋 Processes

#### [process name]
**Why**: [specific reason]
**Maturity Target**: L[level]
**Add to**: `workspace/processes/PROCESSES.json`

---

### 🔌 MCP Servers

#### [server name]
**Why**: [specific reason based on detected services]
**Install**: [install command]

---

### 📁 Workspace Structure

#### [structure recommendation]
**Why**: [specific reason]
**Create**: [paths to create]

---

**Want more?** Ask for additional recommendations for any specific category.

**Want help implementing any of these?** Just ask and the appropriate agent can help set up any of the recommendations above.
```

## Decision Framework

### When to Recommend Cron Jobs
- Recurring tasks that should happen on schedule
- Monitoring and health checks
- Synthesis and reporting
- Memory and knowledge maintenance
- R&D continuous exploration

### When to Recommend Skills
- Frequently repeated prompts or workflows
- Project-specific tasks with templates
- Domain expertise that agents should apply automatically
- Quick actions the user invokes regularly

### When to Recommend Agent Routing Changes
- Tasks consistently going to the wrong agent
- Agents overloaded while others are idle
- New domains or specializations needed
- Quality issues traceable to agent mismatch

### When to Recommend Processes
- Workflows that happen repeatedly without structure
- Quality issues from inconsistent approaches
- Team coordination breakdowns
- Compliance or audit requirements

### When to Recommend MCP Servers
- External service integration needed (databases, APIs)
- Documentation lookup for libraries/SDKs
- Browser automation or testing
- Team tool integration (GitHub, Linear, Slack)

### When to Recommend Workspace Structure
- Files scattered without organization
- Missing communication channels between agents
- No project or sprint tracking
- Knowledge not being captured

---

## Configuration Tips

### Cron Job Setup

```bash
# Add a new cron job
openclaw cron add --name "my-cron" --schedule "0 */6 * * *" --agent cipher --no-deliver --session isolated

# List existing cron jobs
openclaw cron list

# Remove a cron job
openclaw cron remove --name "my-cron"
```

### Agent Dispatch

Cooper handles routing via MoE tags in CLAUDE.md. To update routing:
1. Edit `~/.openclaw/workspace/CLAUDE.md` routing table
2. Update per-agent SOUL.md if role changes
3. Verify with `openclaw doctor`

### Provider-Aware Scheduling

When scheduling cron jobs, consider provider rate limits:
- **Anthropic agents** (Cooper, Pixel, Vault): Stagger by 120s minimum, share OAuth limits
- **DeepSeek agents** (Oracle, Nova, Mirror, Forge, Cipher): No hard limits, safe to overlap
- **MiniMax agents** (Sage, Vista, Anchor, Muse, Vex): 500 RPM, generous limits
- **NIM agents** (Axon, Vigil): 40 RPM free tier, use sparingly

### Headless Mode (for CI/Automation)

```bash
# Run a one-off task
openclaw run --agent forge --task "fix lint errors in src/" --no-deliver

# Scheduled task with model override
openclaw cron add --name "nightly-lint" --schedule "0 3 * * *" --agent forge --model deepseek/deepseek-chat --no-deliver --session isolated
```
