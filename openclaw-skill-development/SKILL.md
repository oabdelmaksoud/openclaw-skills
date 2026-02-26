---
name: openclaw-skill-development
description: "This skill should be used when the user wants to 'create a skill', 'add a skill', 'write a new skill', 'improve skill description', 'organize skill content', or needs guidance on OpenClaw SKILL.md format, progressive disclosure, metadata.openclaw block, or skill development best practices."
metadata:
  {
    "openclaw":
      {
        "emoji": "📖"
      }
  }
---

# Skill Development for OpenClaw

## Overview

Skills are modular, self-contained packages that extend OpenClaw agent capabilities by providing specialized knowledge, workflows, and tools. Skills transform agents from general-purpose assistants into specialized experts equipped with procedural knowledge.

**Key concepts:**
- Skills live in `~/.openclaw/skills/<skill-name>/`
- Each skill requires a `SKILL.md` file with YAML frontmatter
- OpenClaw uses `metadata.openclaw` block for platform-specific metadata
- Progressive disclosure: metadata always loaded, SKILL.md body on trigger, references as needed

## Skill Anatomy

### Directory Structure

```
~/.openclaw/skills/
└── skill-name/
    ├── SKILL.md              # Required: skill definition
    ├── references/           # Optional: detailed documentation
    ├── examples/             # Optional: working examples
    ├── scripts/              # Optional: utility scripts
    └── assets/               # Optional: output resources
```

### SKILL.md Format

```markdown
---
name: skill-name
description: "Describe when this skill should be used"
metadata:
  {
    "openclaw":
      {
        "emoji": "<emoji>"
      }
  }
---

# Skill Name

## Overview
Core principle in 1-2 sentences.

## When to Use
Bullet list with symptoms and use cases.

## Core Pattern
Implementation details and workflows.

## Quick Reference
Tables or bullets for scanning.

## Additional Resources
Pointers to references/, examples/, scripts/
```

### Frontmatter Fields

**name** (required): Unique identifier for the skill
- Use kebab-case: `my-skill-name`
- Letters, numbers, hyphens only
- Max 1024 characters total for frontmatter

**description** (required): When to use this skill
- Use third person: "This skill should be used when..."
- Include specific trigger phrases
- Describe triggering conditions, NOT what the skill does
- Keep under 500 characters

**metadata.openclaw** (recommended): Platform-specific metadata
- `emoji`: Visual identifier for the skill in OpenClaw UI

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata (name + description)** — Always in context (~100 words)
2. **SKILL.md body** — When skill triggers (target 1,500-2,000 words)
3. **Bundled resources** — As needed by agents (unlimited)

### What Goes Where

| Location | Content | When Loaded |
|----------|---------|-------------|
| SKILL.md | Core concepts, essential procedures, quick reference | On trigger |
| references/ | Detailed patterns, advanced techniques, edge cases | As needed |
| examples/ | Complete working examples, templates | As needed |
| scripts/ | Executable utilities, validation tools | On execution |
| assets/ | Templates, images, boilerplate (not loaded into context) | On use |

## Skill Creation Process

### Step 1: Understand the Skill

Identify concrete examples of how the skill will be used:
- What functionality should it support?
- What would a user say that should trigger it?
- Which agents in the roster would benefit most?

### Step 2: Plan Resources

Analyze each example to determine:
- What scripts would be repeatedly rewritten? (-> scripts/)
- What documentation is needed while working? (-> references/)
- What templates or assets are needed? (-> assets/)

### Step 3: Create Structure

```bash
mkdir -p ~/.openclaw/skills/skill-name/{references,examples,scripts}
touch ~/.openclaw/skills/skill-name/SKILL.md
```

### Step 4: Write SKILL.md

**Description best practices:**

```yaml
# GOOD: Third person, specific triggers, no workflow summary
description: "This skill should be used when the user asks to 'create a hook', 'add a scheduled task', or mentions cron job configuration."

# BAD: Summarizes workflow (agents may follow description instead of reading body)
description: "Use when executing plans - dispatches agent per task with review between tasks"

# BAD: Not third person
description: "Use this skill when working with hooks."
```

**Body writing style:**
- Use imperative/infinitive form (verb-first instructions)
- NOT second person ("You should...")
- Keep lean: 1,500-2,000 words
- Move detailed content to references/
- Reference all supporting files explicitly

### Step 5: Validate

- [ ] SKILL.md has valid YAML frontmatter with name and description
- [ ] Description uses third person with specific trigger phrases
- [ ] Body uses imperative form, not second person
- [ ] Body is under 3,000 words (ideally 1,500-2,000)
- [ ] Detailed content moved to references/
- [ ] All referenced files exist
- [ ] metadata.openclaw block includes emoji

### Step 6: Test and Iterate

Test the skill by simulating agent scenarios:
- Does it trigger on expected queries?
- Is the content helpful for intended tasks?
- Are there gaps in the instructions?

## OpenClaw-Specific Considerations

### Agent Roster Integration

Skills in OpenClaw serve 16 agents with different specializations. Consider:
- Which agents will use this skill most frequently?
- Does the skill need different guidance for different agent roles?
- Should the skill reference specific agents by name for routing?

### Workspace Integration

Skills can reference OpenClaw workspace paths:
- `~/.openclaw/workspace/` for shared resources
- `~/.openclaw/workspace/agents-workspaces/<id>/` for agent-specific data
- `~/.openclaw/workspace/processes/PROCESSES.json` for process definitions
- `~/.openclaw/workspace/standards/` for quality standards

### Memory Integration

Skills can leverage OpenClaw's memory system:
- LanceDB at `~/.openclaw/memory/lancedb/` for semantic search
- SHARED_KNOWLEDGE.json for cross-agent knowledge
- Reference memory contents when relevant to skill domain

## Common Mistakes

### Weak Trigger Description
```yaml
# BAD
description: "Provides guidance for working with automation."
# GOOD
description: "This skill should be used when the user asks to 'create a cron job', 'define a process', or 'automate agent tasks'."
```

### Too Much in SKILL.md
Keep SKILL.md lean. Move detailed content to references/:
```
# BAD: 8,000 words all in SKILL.md
# GOOD: 1,800 words in SKILL.md + 2,500 in references/patterns.md
```

### Missing Resource References
Always tell agents where to find additional information:
```markdown
## Additional Resources
- **`references/patterns.md`** — Detailed patterns
- **`examples/working-example.sh`** — Complete example
```

## Quick Reference

### Minimal Skill
```
skill-name/
└── SKILL.md
```

### Standard Skill (Recommended)
```
skill-name/
├── SKILL.md
├── references/
│   └── detailed-guide.md
└── examples/
    └── working-example.sh
```

### Complete Skill
```
skill-name/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
├── examples/
│   ├── example1.sh
│   └── example2.json
└── scripts/
    └── validate.sh
```

## Additional Resources

### Reference Files
- **`references/skill-creator-original.md`** — Full original skill creation methodology
