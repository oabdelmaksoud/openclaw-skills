---
name: agi-farm
description: >
  Interactive setup wizard that creates a fully working multi-agent AI team workspace.
  Generates agents, SOUL.md files, comms infrastructure, cron jobs, and a portable
  GitHub bundle — all customized to the user's team name and size.
  Use when: setting up a new multi-agent system from scratch, onboarding a new OpenClaw
  instance, or sharing a reusable AGI team with others.
  Commands: setup | status | rebuild | export
---

# agi-farm — Multi-Agent Team Setup Wizard

Builds a complete customizable multi-agent AI team on top of OpenClaw.
Choose your team size (3/5/9 agents), name your orchestrator, pick your
collaboration frameworks — get a live workspace + portable GitHub bundle.

## Commands

| Command | What it does |
|---|---|
| `/agi-farm setup` | Run full wizard — creates agents, workspace, bundle, GitHub |
| `/agi-farm status` | Show team health (agents, tasks, cron status) |
| `/agi-farm rebuild` | Regenerate workspace from existing bundle |
| `/agi-farm export` | Push current bundle to GitHub |

---

## `/agi-farm setup` — Full Wizard Protocol

Follow these steps exactly. **Ask one question at a time.** Do not proceed until you have a confirmed answer.

---

### Step 1 — Team name

Ask:
> "What should we call your team? (e.g. NovaCorp, TradingDesk, ResearchLab)"

Store as `TEAM_NAME`. Default: `MyTeam` if user says skip.

---

### Step 2 — Orchestrator name

Ask:
> "What's your orchestrator's name? (default: Cooper)"

Store as `ORCHESTRATOR_NAME`. Default: `Cooper`.

---

### Step 3 — Team size preset

Ask:
> "How many agents do you want?
>
> **3** — Minimal: Orchestrator + Researcher + Builder
> **5** — Standard: adds QA Engineer + Content Specialist
> **9** — Full stack: complete 9-agent AGI system (recommended)
>
> Enter 3, 5, or 9:"

Store as `PRESET`.

---

### Step 4 — Frameworks

Ask:
> "Which collaboration frameworks do you want installed?
>
> **autogen** — Round-robin debate until consensus
> **crewai** — Structured pipelines with explicit task outputs
> **langgraph** — Stateful graphs with dynamic routing
> **all** — Install all three (recommended)
> **none** — Skip frameworks for now
>
> Enter one or more (comma-separated), or 'all' / 'none':"

Parse into a list. `all` → `["autogen", "crewai", "langgraph"]`. Store as `FRAMEWORKS`.

---

### Step 5 — GitHub

Ask:
> "Should I create a GitHub repo for your portable bundle?
>
> **yes** — Create github.com/<your-username>/agi-farm-<team-name-lower>
> **no** — Save bundle locally only"

Store as `CREATE_GITHUB` (yes/no).

---

### Step 6 — Confirm

Show summary and ask for confirmation:

```
Ready to build your {{TEAM_NAME}} team:
  Orchestrator: {{ORCHESTRATOR_NAME}}
  Team size: {{PRESET}} agents
  Frameworks: {{FRAMEWORKS}}
  GitHub: {{CREATE_GITHUB}}

Shall I proceed? (yes/no)
```

If no → restart from Step 1.
If yes → execute Steps 7–15.

---

### Step 7 — Write `team.json`

Create `~/.openclaw/workspace/agi-farm-bundle/` and write `team.json`:

```bash
mkdir -p ~/.openclaw/workspace/agi-farm-bundle/
```

Write `team.json` with the agent roster based on preset:

**3-agent roster:**
```json
{
  "team_name": "<TEAM_NAME>",
  "orchestrator_name": "<ORCHESTRATOR_NAME>",
  "preset": "3",
  "frameworks": <FRAMEWORKS_JSON>,
  "created_at": "<ISO_TIMESTAMP>",
  "agents": [
    {"id": "main", "name": "<ORCHESTRATOR_NAME>", "emoji": "🦅", "role": "Orchestrator", "goal": "Orchestrate the team, delegate tasks, synthesize results", "model": "anthropic/claude-sonnet-4-6", "workspace": "."},
    {"id": "researcher", "name": "Sage", "emoji": "🔮", "role": "Researcher", "goal": "Research deeply and surface the insights that matter most", "model": "gemini/gemini-2.0-pro-exp", "workspace": "researcher"},
    {"id": "builder", "name": "Forge", "emoji": "⚒️", "role": "Builder", "goal": "Implement solutions cleanly and efficiently", "model": "openai/glm-5", "workspace": "builder"}
  ]
}
```

**5-agent roster:** add to 3-agent:
```json
    {"id": "qa", "name": "Vigil", "emoji": "🛡️", "role": "QA Engineer", "goal": "Ensure every output meets quality standards before delivery", "model": "openai/glm-4.7-flash", "workspace": "qa"},
    {"id": "content", "name": "Anchor", "emoji": "⚓", "role": "Content Specialist", "goal": "Craft clear content that communicates complex ideas simply", "model": "minimax-portal/MiniMax-M2.5", "workspace": "content"}
```

**9-agent roster:** use full Cooper stack:
```json
[
  {"id": "main", "name": "<ORCHESTRATOR_NAME>", "emoji": "🦅", "role": "Orchestrator", "goal": "Orchestrate specialists, delegate tasks, synthesize results", "model": "anthropic/claude-sonnet-4-6", "workspace": "."},
  {"id": "sage", "name": "Sage", "emoji": "🔮", "role": "Solution Architect", "goal": "Design robust, scalable architectures", "model": "anthropic/claude-sonnet-4-6", "workspace": "solution-architect"},
  {"id": "forge", "name": "Forge", "emoji": "⚒️", "role": "Implementation Engineer", "goal": "Implement clean, well-tested code efficiently", "model": "openai/glm-5", "workspace": "implementation-engineer"},
  {"id": "pixel", "name": "Pixel", "emoji": "🐛", "role": "Debugger", "goal": "Find the true root cause of any bug or failure", "model": "anthropic/claude-opus-4-6", "workspace": "debugger"},
  {"id": "vista", "name": "Vista", "emoji": "🔭", "role": "Business Analyst", "goal": "Research deeply and surface the insights that matter most", "model": "gemini/gemini-2.0-pro-exp", "workspace": "business-analyst"},
  {"id": "cipher", "name": "Cipher", "emoji": "🔊", "role": "Knowledge Curator", "goal": "Curate and surface knowledge so the team never forgets", "model": "gemini/gemini-2.0-pro-exp", "workspace": "knowledge-curator"},
  {"id": "vigil", "name": "Vigil", "emoji": "🛡️", "role": "Quality Assurance Engineer", "goal": "Ensure every output meets quality standards", "model": "openai/glm-4.7-flash", "workspace": "quality-assurance"},
  {"id": "anchor", "name": "Anchor", "emoji": "⚓", "role": "Content Specialist", "goal": "Craft clear content that communicates complex ideas simply", "model": "minimax-portal/MiniMax-M2.5", "workspace": "content-specialist"},
  {"id": "lens", "name": "Lens", "emoji": "📡", "role": "Multimodal Specialist", "goal": "Extract meaning from images, documents, and multimodal inputs", "model": "gemini/gemini-2.0-pro-exp", "workspace": "multimodal-specialist"}
]
```

---

### Step 8 — Generate workspace files

```bash
python3 ~/.openclaw/skills/agi-farm/generate.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json \
  --output ~/.openclaw/workspace/ \
  --all-agents --shared --bundle
```

Report any errors. If templates are missing for specific agents, the generic template is used automatically.

---

### Step 9 — Create OpenClaw agents

For each agent **except `main`** (main already exists as the current assistant):

```bash
openclaw agents add \
  --agent <agent-id> \
  --name "<agent-name>" \
  --emoji "<emoji>" \
  --model "<model>" \
  --workspace "~/.openclaw/workspace/agents-workspaces/<workspace>"
```

If an agent already exists, skip it (don't error).

---

### Step 10 — Register cron jobs

```bash
# Morning standup
openclaw cron add \
  --name "<TEAM_NAME_LOWER>-morning-standup" \
  --description "Daily morning standup for {{TEAM_NAME}} team" \
  --agent main --cron "0 8 * * *" --tz "America/Detroit" \
  --session isolated \
  --message "Morning standup: read TASKS.json, check agent status, plan the day. Report key items." \
  --timeout-seconds 120

# Heartbeat (every 30 min)
openclaw cron add \
  --name "<TEAM_NAME_LOWER>-heartbeat" \
  --description "Team health heartbeat every 30 min" \
  --agent main --cron "*/30 * * * *" --tz "America/Detroit" \
  --session isolated \
  --message "Heartbeat check: verify all agents available, flag any stuck tasks." \
  --timeout-seconds 60 --no-deliver
```

---

### Step 11 — Install selected frameworks

For each framework in `FRAMEWORKS` (`autogen-collab`, `crewai-collab`, `langgraph-collab`):

```bash
# Check if installed
if [ ! -d ~/.openclaw/skills/<framework>-collab ]; then
  echo "Installing <framework>-collab..."
  # Sparse clone
  TMP=$(mktemp -d)
  git clone --depth 1 --filter=blob:none --sparse \
    https://github.com/oabdelmaksoud/openclaw-skills.git "$TMP"
  cd "$TMP"
  git sparse-checkout set <framework>-collab
  cp -r <framework>-collab ~/.openclaw/skills/
  rm -rf "$TMP"
  # Run setup
  ~/.openclaw/skills/<framework>-collab/setup.sh
  echo "<framework>-collab installed."
else
  echo "<framework>-collab already installed. Skipping."
fi

# Build agent configs
python3 ~/.openclaw/skills/<framework>-collab/build_agents.py --force 2>/dev/null || \
python3 ~/.openclaw/skills/<framework>-collab/build_personas.py --force 2>/dev/null || true
```

---

### Step 12 — Initialize git + push bundle (if GitHub chosen)

```bash
cd ~/.openclaw/workspace/agi-farm-bundle
git init -b main
git add .
git commit -m "feat: <TEAM_NAME> AGI farm — initial bundle"

# Create GitHub repo
gh repo create agi-farm-<TEAM_NAME_LOWER> \
  --public \
  --description "<TEAM_NAME> AGI team bundle — built with agi-farm" \
  --source . --remote origin --push

echo "Bundle pushed to: https://github.com/$(gh api user --jq .login)/agi-farm-<TEAM_NAME_LOWER>"
```

If user chose no GitHub: skip this step.

---

### Step 13 — Commit workspace

```bash
cd ~/.openclaw/workspace
git add -A
git commit -m "feat: <TEAM_NAME> AGI team — agi-farm setup complete (preset: <PRESET>)"
```

---

### Step 14 — Initialize JSON registries

Write minimal versions of required registries:

```bash
# TASKS.json
echo '[]' > ~/.openclaw/workspace/TASKS.json

# AGENT_STATUS.json — one entry per agent
python3 -c "
import json, sys
from pathlib import Path
team = json.loads(Path('$HOME/.openclaw/workspace/agi-farm-bundle/team.json').read_text())
status = {a['id']: {'status': 'available', 'name': a['name']} for a in team['agents']}
Path('$HOME/.openclaw/workspace/AGENT_STATUS.json').write_text(json.dumps(status, indent=2))
print('AGENT_STATUS.json written')
"
```

---

### Step 15 — Report success

```
✅ {{TEAM_NAME}} AGI team is live!

Agents: {{PRESET}} ({{AGENT_NAMES_LIST}})
Frameworks: {{FRAMEWORKS}}
Workspace: ~/.openclaw/workspace/
Bundle: ~/.openclaw/workspace/agi-farm-bundle/
GitHub: https://github.com/<user>/agi-farm-<team-name-lower> (if created)

Next steps:
- Talk to your orchestrator ({{ORCHESTRATOR_NAME}}) directly
- Check team health: /agi-farm status
- Assign your first task via: /agi-farm task
```

---

## `/agi-farm status` Protocol

```bash
echo "=== {{TEAM_NAME}} Team Status ==="

# Agent status
python3 -c "
import json
from pathlib import Path
p = Path('$HOME/.openclaw/workspace/AGENT_STATUS.json')
if p.exists():
    d = json.loads(p.read_text())
    for aid, info in d.items():
        print(f'  {info[\"name\"]} ({aid}): {info[\"status\"]}')
else:
    print('  No AGENT_STATUS.json found')
"

# Pending tasks
python3 -c "
import json
from pathlib import Path
p = Path('$HOME/.openclaw/workspace/TASKS.json')
if p.exists():
    tasks = json.loads(p.read_text())
    pending = [t for t in tasks if t.get('status') == 'pending']
    print(f'  Tasks: {len(tasks)} total, {len(pending)} pending')
else:
    print('  No TASKS.json found')
"

# Cron jobs
openclaw cron list 2>/dev/null | grep -E "standup|heartbeat|cleanup" | head -10
```

---

## `/agi-farm rebuild` Protocol

```bash
python3 ~/.openclaw/skills/agi-farm/generate.py \
  --team-json ~/.openclaw/workspace/agi-farm-bundle/team.json \
  --output ~/.openclaw/workspace/ \
  --all-agents --shared

echo "Workspace rebuilt from bundle."
echo "Re-run agent creation if needed (Step 9 of setup)."
```

---

## `/agi-farm export` Protocol

```bash
cd ~/.openclaw/workspace/agi-farm-bundle
git add -A
git commit -m "export: updated bundle $(date +%Y-%m-%d)" 2>/dev/null || echo "Nothing to commit"
git push 2>/dev/null || echo "No remote configured — run /agi-farm setup first"
echo "Export complete."
```
