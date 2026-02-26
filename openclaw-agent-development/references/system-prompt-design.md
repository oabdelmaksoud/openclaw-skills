# System Prompt Design for OpenClaw Agents

## Overview

In OpenClaw, agent behavior is defined through two files:
- **IDENTITY.md** — Per-agent identity, role, and behavioral traits
- **SOUL.md** — Shared instructions read by ALL agents

This guide covers patterns for writing effective IDENTITY.md and SOUL.md content.

## IDENTITY.md Structure

Every agent IDENTITY.md should follow this template:

```markdown
# Agent: <DisplayName>

## Role
<Specific role in 1-2 sentences>

## Primary Responsibilities
1. <Primary responsibility — the main task>
2. <Secondary responsibility>
3. <Additional responsibilities>

## Domain Expertise
- <Expertise area 1>
- <Expertise area 2>

## Behavioral Traits
- <Communication style>
- <Decision-making approach>
- <Interaction patterns>

## Quality Standards
- <Standard 1>
- <Standard 2>

## Output Format
<What the agent typically produces and how to structure it>

## Edge Cases
- <Edge case 1>: <How to handle>
- <Edge case 2>: <How to handle>

## Idle-Time Standing Orders
When queue and backlog are empty:
1. <Standing order 1>
2. <Standing order 2>
```

## Writing Style Guidelines

### Tone and Voice

Write in second person, addressing the agent directly:
```
You are responsible for...
You will analyze...
Your process should...
```

### Clarity and Specificity

Be specific, not vague:
```
# GOOD
Check for SQL injection by examining all database queries for parameterization

# BAD
Look for security issues
```

### Actionable Instructions

Give concrete steps:
```
# GOOD
Read the file, search for patterns using grep, then validate findings

# BAD
Analyze the code
```

## SOUL.md Patterns

SOUL.md is shared across ALL 16 agents. It should contain:

1. **Core protocols** — Communication and coordination rules
2. **Task handling** — How to pick up, execute, and close tickets
3. **Quality standards** — Rating scale, delivery criteria
4. **File-based orchestration** — How to use comms/, TASKS.json, broadcast.md
5. **Idle-time behavior** — Default actions when queue is empty

### Keep SOUL.md Focused

- Only shared instructions belong in SOUL.md
- Agent-specific behavior goes in IDENTITY.md
- Do not duplicate information between the two files
- Target under 10,000 characters

## Pattern: Analysis Agents

For agents that analyze code, security, or architecture (Pixel, Vault, Sage):

```markdown
## Analysis Process
1. **Gather Context**: Read relevant files and logs
2. **Initial Scan**: Identify obvious issues
3. **Deep Analysis**: Examine specific aspects
4. **Synthesize Findings**: Group related issues
5. **Prioritize**: Rank by severity/impact
6. **Generate Report**: Format according to output template
```

## Pattern: Generation Agents

For agents that create content, code, or documentation (Forge, Anchor, Muse):

```markdown
## Generation Process
1. **Understand Requirements**: Analyze what needs to be created
2. **Gather Context**: Read existing patterns and standards
3. **Design Structure**: Plan architecture/organization
4. **Generate Content**: Create output following standards
5. **Validate**: Verify correctness and completeness
6. **Document**: Add comments and explanations
```

## Pattern: Orchestration Agents

For agents that coordinate workflows (Cooper):

```markdown
## Orchestration Process
1. **Plan**: Understand full workflow and dependencies
2. **Triage**: Assign story points, due dates, sprint
3. **Dispatch**: Route to appropriate agent via inbox
4. **Monitor**: Track progress via TASKS.json
5. **Quality Gate**: Ensure Vigil rating >= 3
6. **Close**: Update ticket to Done with metrics
```

## Common Pitfalls

### Vague Responsibilities
```
# BAD
Help with code

# GOOD  
Analyze TypeScript code for type safety issues, identify missing annotations, recommend improvements
```

### Missing Process Steps
```
# BAD
Analyze the code and provide feedback.

# GOOD
1. Read code files
2. Scan for type annotations
3. Check for 'any' usage
4. Verify generic parameters
5. List findings with file:line references
```

### Undefined Output Format
```
# BAD
Provide a report.

# GOOD
## Output Format
1. Summary (2-3 sentences)
2. Critical Issues (must fix)
3. Major Issues (should fix)
4. Minor Issues (consider fixing)
5. Positive Observations
```

## Length Guidelines

- **IDENTITY.md**: 500-2,000 words (focused on role)
- **SOUL.md**: 2,000-5,000 words (shared instructions)
- **Avoid > 10,000 characters**: Diminishing returns, context pollution
