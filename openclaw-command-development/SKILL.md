---
name: openclaw-command-development
description: "This skill should be used when the user asks to 'create a slash command', 'add a command', 'write a custom command', 'define command arguments', 'skill slash-commands', 'organize commands', or needs guidance on OpenClaw skill-based slash commands, YAML frontmatter, dynamic arguments, or command development best practices."
metadata:
  {
    "openclaw":
      {
        "emoji": "💻"
      }
  }
---

# Command Development for OpenClaw

## Overview

OpenClaw skills can include slash commands defined as Markdown files. These commands provide reusable, standardized prompts that agents execute during interactive sessions.

**Key concepts:**
- Markdown file format with optional YAML frontmatter
- Dynamic arguments and file references
- Skill-based organization in `~/.openclaw/skills/`
- Commands are instructions FOR agents, not messages TO users

## Command Basics

### What is a Slash Command?

A slash command is a Markdown file containing a prompt that an OpenClaw agent executes when invoked. Commands provide:
- **Reusability**: Define once, use repeatedly
- **Consistency**: Standardize common workflows
- **Sharing**: Distribute across the agent roster
- **Efficiency**: Quick access to complex multi-step prompts

### Critical: Commands are Instructions FOR Agents

When a command is invoked, its content becomes the agent's instructions. Write commands as directives TO the agent:

**Correct (instructions for agent):**
```markdown
Review this code for security vulnerabilities including:
- SQL injection
- XSS attacks
- Authentication issues

Provide specific line numbers and severity ratings.
```

**Incorrect (messages to user):**
```markdown
This command will review your code for security issues.
```

### Command Locations

**Personal commands** (available everywhere):
- Location: `~/.openclaw/skills/<skill-name>/commands/`
- Scope: Available in all agent sessions

**Workspace commands** (shared with all agents):
- Location: `~/.openclaw/workspace/commands/`
- Scope: Available to all 16 agents in the roster

## File Format

### Basic Structure

```
~/.openclaw/skills/my-skill/
└── commands/
    ├── review.md           # /review command
    ├── test.md             # /test command
    └── deploy.md           # /deploy command
```

**Simple command (no frontmatter needed):**
```markdown
Review this code for security vulnerabilities including:
- SQL injection
- XSS attacks
- Authentication bypass
```

### With YAML Frontmatter

```markdown
---
description: Review code for security issues
allowed-tools: Read, Grep, Bash(git:*)
---

Review this code for security vulnerabilities...
```

## Frontmatter Fields

### description
Brief description shown in help output.
```yaml
description: Review pull request for code quality
```

### allowed-tools
Specify which tools the command can use.
```yaml
allowed-tools: Read, Write, Edit, Bash(git:*)
```

### argument-hint
Document expected arguments for autocomplete.
```yaml
argument-hint: [file-path] [priority]
```

## Dynamic Arguments

### Using $ARGUMENTS

Capture all arguments as a single string:

```markdown
---
description: Fix issue by number
argument-hint: [issue-number]
---

Fix issue #$ARGUMENTS following our coding standards.
```

### Positional Arguments ($1, $2, $3)

```markdown
---
description: Review PR with priority
argument-hint: [pr-number] [priority]
---

Review pull request #$1 with priority level $2.
```

## File References

### Using @ Syntax

Include file contents in command:

```markdown
---
description: Review specific file
argument-hint: [file-path]
---

Review @$1 for code quality and best practices.
```

## Integration with OpenClaw Agents

### Dispatching Commands to Specific Agents

Commands can be routed to specific agents in the 16-agent roster:

```markdown
---
description: Deep security audit
---

Route this to Vault (cybersecurity agent) for analysis.

openclaw agent spawn --agent cybersecurity --task "Perform deep security audit on recent changes"
```

### Multi-Agent Workflow Commands

```markdown
---
description: Full review pipeline
argument-hint: [file-path]
---

Phase 1: Route to Sage (solution-architect) for design review
Phase 2: Route to Vault (cybersecurity) for security analysis
Phase 3: Route to Vex (tester) for test coverage assessment

Target: @$1
```

## Command Organization

### Flat Structure
```
commands/
├── build.md
├── test.md
├── deploy.md
└── review.md
```

### Namespaced Structure
```
commands/
├── ci/
│   ├── build.md
│   └── test.md
├── git/
│   ├── commit.md
│   └── pr.md
└── docs/
    └── generate.md
```

## Best Practices

1. **Single responsibility**: One command, one task
2. **Clear descriptions**: Self-explanatory
3. **Document arguments**: Always provide `argument-hint`
4. **Consistent naming**: Use verb-noun pattern (review-pr, fix-issue)
5. **Agent-aware**: Specify which agent(s) should handle when relevant
6. **Workspace paths**: Use `~/.openclaw/` paths, never hardcoded absolute paths

## Common Patterns

### Review Pattern
```markdown
---
description: Review code changes
allowed-tools: Read, Bash(git:*)
---

Review each changed file for:
1. Code quality and style
2. Potential bugs
3. Test coverage
4. Documentation needs
```

### Agent Dispatch Pattern
```markdown
---
description: Spawn analysis task
argument-hint: [task-description]
---

openclaw agent spawn --task "$ARGUMENTS"
```

## Additional Resources

### Reference Files
- **`references/frontmatter-reference.md`** — Complete frontmatter field specifications
- **`references/advanced-workflows.md`** — Multi-step and multi-agent command patterns

### Example Files
- **`examples/simple-commands.md`** — Basic command examples
- **`examples/plugin-commands.md`** — Skill-integrated command patterns
