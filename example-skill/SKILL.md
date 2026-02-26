---
name: example-skill
description: "This skill should be used when the user asks to 'demonstrate skills', 'show skill format', 'create a skill template', or discusses skill development patterns. Provides a reference template for creating OpenClaw skills."
metadata:
  {
    "openclaw":
      {
        "emoji": "📋"
      }
  }
---

# Example Skill

This skill demonstrates the structure and format for OpenClaw skills.

## Overview

Skills are capabilities that OpenClaw agents autonomously use based on task context. Skills provide contextual guidance that agents incorporate into their responses. Skills are stored in `~/.openclaw/skills/` and are available to all agents in the roster.

## When This Skill Applies

This skill activates when the user's request involves:
- Creating or understanding OpenClaw skills
- Skill template or reference needs
- Skill development patterns

## Skill Structure

### Required Files

```
skills/
└── skill-name/
    └── SKILL.md          # Main skill definition (required)
```

### Optional Supporting Files

```
skills/
└── skill-name/
    ├── SKILL.md          # Main skill definition
    ├── README.md         # Additional documentation
    ├── references/       # Reference materials
    │   └── patterns.md
    ├── examples/         # Example files
    │   └── sample.md
    └── scripts/          # Helper scripts
        └── helper.sh
```

## OpenClaw Frontmatter Format

Skills use YAML frontmatter with the OpenClaw metadata block:

```yaml
---
name: my-skill-name
description: "When to use this skill and what it does. Include trigger phrases and contexts."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔧"
      }
  }
---
```

### Frontmatter Fields

- **name** (required): Skill identifier
- **description** (required): Trigger conditions — describe when the skill should be used
- **metadata.openclaw.emoji** (recommended): Emoji icon for the skill

## Writing Effective Descriptions

The description field is crucial — it tells OpenClaw agents when to invoke the skill.

**Good description patterns:**
```yaml
description: "This skill should be used when the user asks to 'specific phrase', 'another phrase', mentions 'keyword', or discusses topic-area."
```

**Include:**
- Specific trigger phrases users might say
- Keywords that indicate relevance
- Topic areas the skill covers

## Skill Content Guidelines

1. **Clear purpose**: State what the skill helps with
2. **When to use**: Define activation conditions
3. **Structured guidance**: Organize information logically
4. **Actionable instructions**: Provide concrete steps
5. **Examples**: Include practical examples when helpful

## Best Practices

- Keep skills focused on a single domain
- Write descriptions that clearly indicate when to activate
- Include reference materials in subdirectories for complex skills
- Test that the skill activates for expected queries
- Avoid overlap with other skills' trigger conditions
- Skills in `~/.openclaw/skills/` are available system-wide to all 16 agents
