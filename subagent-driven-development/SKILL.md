---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
metadata:
  {
    "openclaw":
      {
        "emoji": "⚙️"
      }
  }
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

## When to Use

**vs. Executing Plans (parallel session):**
- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Two-stage review after each task: spec compliance first, then code quality
- Faster iteration (no human-in-loop between tasks)

## The Process

1. Read plan, extract all tasks with full text, note context, create TodoWrite
2. Per task:
   - Dispatch implementer subagent (see `references/implementer-prompt.md`)
   - If implementer asks questions, answer them, then re-dispatch
   - Implementer implements, tests, commits, self-reviews
   - Dispatch spec reviewer subagent (see `references/spec-reviewer-prompt.md`)
   - If spec reviewer finds issues, implementer fixes, re-review
   - Dispatch code quality reviewer subagent (see `references/code-quality-reviewer-prompt.md`)
   - If quality reviewer finds issues, implementer fixes, re-review
   - Mark task complete in TodoWrite
3. After all tasks, dispatch final code reviewer for entire implementation
4. Use finishing-a-development-branch skill

## Prompt Templates

- `references/implementer-prompt.md` - Dispatch implementer subagent
- `references/spec-reviewer-prompt.md` - Dispatch spec compliance reviewer subagent
- `references/code-quality-reviewer-prompt.md` - Dispatch code quality reviewer subagent

## Advantages

**vs. Manual execution:**
- Subagents follow TDD naturally
- Fresh context per task (no confusion)
- Parallel-safe (subagents don't interfere)
- Subagent can ask questions (before AND during work)

**Quality gates:**
- Self-review catches issues before handoff
- Two-stage review: spec compliance, then code quality
- Review loops ensure fixes actually work
- Spec compliance prevents over/under-building
- Code quality ensures implementation is well-built

## Red Flags

**Never:**
- Start implementation on main/master branch without explicit user consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementation subagents in parallel (conflicts)
- Make subagent read plan file (provide full text instead)
- Skip scene-setting context (subagent needs to understand where task fits)
- **Start code quality review before spec compliance passes**
- Move to next task while either review has open issues

**If subagent asks questions:**
- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

**If reviewer finds issues:**
- Implementer (same subagent) fixes them
- Reviewer reviews again
- Repeat until approved

## Integration

**Required workflow skills:**
- **using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **writing-plans** - Creates the plan this skill executes
- **requesting-code-review** - Code review template for reviewer subagents
- **finishing-a-development-branch** - Complete development after all tasks

**Subagents should use:**
- **test-driven-development** - Subagents follow TDD for each task

**Alternative workflow:**
- **executing-plans** - Use for parallel session instead of same-session execution
