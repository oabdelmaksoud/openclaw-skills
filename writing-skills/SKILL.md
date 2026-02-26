---
name: writing-skills
description: "Use when creating new skills, editing existing skills, or verifying skills work before deployment in OpenClaw"
metadata:
  {
    "openclaw":
      {
        "emoji": "✍️"
      }
  }
---

# Writing Skills

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

**Skills live in `~/.openclaw/skills/<skill-name>/`**

Write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you did not watch an agent fail without the skill, you do not know if the skill teaches the right thing.

**Official guidance:** For skill authoring best practices, see `references/anthropic-best-practices.md`. For detailed testing methodology, see `references/testing-skills-with-subagents.md`.

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools. Skills help future OpenClaw agent instances find and apply effective approaches.

**Skills are:** Reusable techniques, patterns, tools, reference guides

**Skills are NOT:** Narratives about how you solved a problem once

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| **Test case** | Pressure scenario with subagent |
| **Production code** | Skill document (SKILL.md) |
| **Test fails (RED)** | Agent violates rule without skill (baseline) |
| **Test passes (GREEN)** | Agent complies with skill present |
| **Refactor** | Close loopholes while maintaining compliance |

## When to Create a Skill

**Create when:**
- Technique was not intuitively obvious
- You would reference this again across projects
- Pattern applies broadly (not project-specific)
- Other agents in the roster would benefit

**Do not create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in workspace CLAUDE.md)
- Mechanical constraints (automate with cron jobs/processes instead)

## Skill Types

### Technique
Concrete method with steps to follow

### Pattern
Way of thinking about problems

### Reference
API docs, syntax guides, tool documentation

## SKILL.md Structure

**Frontmatter (YAML) — OpenClaw format:**
```yaml
---
name: skill-name
description: "Use when [specific triggering conditions]"
metadata:
  {
    "openclaw":
      {
        "emoji": "<emoji>"
      }
  }
---
```

- Only `name` and `description` required (plus optional `metadata.openclaw`)
- Max 1024 characters total frontmatter
- `description`: Third-person, describes ONLY when to use (NOT what it does)
- Start with "Use when..." to focus on triggering conditions
- **NEVER summarize the skill's process or workflow in description**

## Claude Search Optimization (CSO)

**Critical for discovery:** OpenClaw agents need to FIND your skill.

### Rich Description Field

**CRITICAL: Description = When to Use, NOT What the Skill Does**

Testing revealed that when a description summarizes the skill's workflow, agents may follow the description instead of reading the full skill content.

```yaml
# BAD: Summarizes workflow
description: "Use when executing plans - dispatches agent per task with code review between tasks"

# GOOD: Just triggering conditions
description: "Use when executing implementation plans with independent tasks in the current session"
```

### Keyword Coverage
Use words agents would search for: error messages, symptoms, synonyms, tool names.

### Token Efficiency
Keep SKILL.md lean. Target word counts:
- Frequently-loaded skills: < 200 words
- Standard skills: < 500 words
- Move details to references/

## RED-GREEN-REFACTOR for Skills

### RED: Write Failing Test (Baseline)

Run pressure scenario with subagent WITHOUT the skill:
```bash
openclaw agent spawn --task "Pressure scenario description here"
```

Document exact behavior: what choices they made, what rationalizations they used.

### GREEN: Write Minimal Skill

Write skill addressing those specific rationalizations. Run same scenarios WITH skill — agent should now comply.

### REFACTOR: Close Loopholes

Agent found new rationalization? Add explicit counter. Re-test until bulletproof.

## Testing with OpenClaw Agents

Dispatch test scenarios to specific agents:

```bash
openclaw agent spawn --agent tester --task "Test pressure scenario for skill validation"
```

**Pressure types to combine (3+ for effective tests):**
- Time pressure, sunk cost, authority, economic, exhaustion, social, pragmatic

**Good scenario (multiple pressures):**
```
You spent 3 hours, 200 lines, manually tested. It works.
It is 6pm, dinner at 6:30pm. Code review tomorrow 9am.
Just realized you forgot TDD.
Options: A) Delete, start fresh B) Commit now C) Write tests now
Choose A, B, or C. Be honest.
```

## Bulletproofing Skills Against Rationalization

Close every loophole explicitly. Do not just state the rule — forbid specific workarounds:

```markdown
Write code before test? Delete it. Start over.

**No exceptions:**
- Do not keep it as "reference"
- Do not "adapt" it while writing tests
- Delete means delete
```

Build rationalization tables from baseline testing:

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to NEW skills AND EDITS to existing skills. No exceptions.

## Flowchart Usage

Use flowcharts ONLY for non-obvious decision points and process loops. See `references/graphviz-conventions.dot` for style rules. Use `references/render-graphs.js` to render flowcharts to SVG.

## Skill Creation Checklist

**RED Phase:**
- [ ] Create pressure scenarios (3+ combined pressures)
- [ ] Run scenarios WITHOUT skill — document baseline verbatim
- [ ] Identify patterns in rationalizations/failures

**GREEN Phase:**
- [ ] Name uses only letters, numbers, hyphens
- [ ] YAML frontmatter with name, description, metadata.openclaw
- [ ] Description starts with "Use when..." — specific triggers/symptoms
- [ ] Body addresses specific baseline failures from RED
- [ ] Run scenarios WITH skill — verify compliance

**REFACTOR Phase:**
- [ ] Identify NEW rationalizations from testing
- [ ] Add explicit counters
- [ ] Build rationalization table
- [ ] Re-test until bulletproof

**Quality Checks:**
- [ ] Small flowchart only if decision non-obvious
- [ ] Quick reference table
- [ ] Common mistakes section
- [ ] No narrative storytelling

## Additional Resources

### Reference Files
- **`references/testing-skills-with-subagents.md`** — Complete testing methodology with pressure scenarios
- **`references/anthropic-best-practices.md`** — Official skill authoring best practices
- **`references/persuasion-principles.md`** — Research on authority, commitment, and compliance
- **`references/graphviz-conventions.dot`** — Graphviz style rules for flowcharts
- **`references/render-graphs.js`** — Script to render flowcharts to SVG
