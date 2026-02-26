# Agent Dispatch and Routing in OpenClaw

## Overview

In OpenClaw, agents are dispatched via the tag-based MoE (Mixture of Experts) routing system. This guide covers when and how to route tasks to specific agents.

## Dispatch Methods

### Direct Spawn

Dispatch a task to a specific agent:
```bash
openclaw agent spawn --agent <agent-id> --task "Task description"
```

### Cooper-Routed (Recommended)

Let Cooper (orchestrator) route based on task tags:
```bash
openclaw agent spawn --task "Task description with domain keywords"
```

Cooper auto-assigns based on MoE tag matching to the appropriate agent.

### Inbox-Based (Inter-Agent)

Agents can request work from other agents by writing to their inbox:
```markdown
# Write to workspace/comms/inboxes/<target-agent-id>.md
## Request from <source-agent>
**Priority**: High
**Task**: <description>
**Context**: <relevant details>
**Deadline**: <if applicable>
```

## Agent Routing Guide

| Domain | Route To | Agent ID | Why |
|--------|----------|----------|-----|
| Debugging, RCA | Pixel | debugger | Root cause analysis expert |
| Security, threats | Vault | cybersecurity | Security specialist |
| Architecture, design | Sage | solution-architect | Design patterns expert |
| Predictions, foresight | Oracle | predictive-analyst | Hypothesis generation |
| R&D, research | Nova | nova | R&D lead (never regular tickets) |
| Self-reflection | Mirror | metacognition | Metacognitive analysis |
| Business analysis | Vista | business-analyst | Requirements and research |
| Implementation | Forge | implementation | Coding and tool building |
| Testing, QA | Vex | tester | Adversarial testing |
| Infrastructure | Axon | devops | CI/CD and deployment |
| Quality monitoring | Vigil | quality-assurance | Quality gate enforcement |
| Content writing | Anchor | content-specialist | User-facing content |
| Creative ideation | Muse | creativity | Creative content |
| Knowledge management | Cipher | knowledge-curator | Memory synthesis |
| Multimodal tasks | Lens | multimodal | Images, voice, web search |

## Routing Best Practices

1. **Tag-based dispatch**: Include domain keywords in task descriptions
2. **Never assign regular tickets to Nova**: R&D-only agent
3. **Stagger Anthropic agents**: Cooper, Pixel, Vault share rate limits — never dispatch concurrently
4. **Use subagent self-closure**: Each agent updates its own ticket to Done as last action
5. **Max 1 dispatch per cron run**: Prevents race conditions on tickets.json
6. **Monitor stale sessions**: Gateway kills sessions after ~1 hour for complex tasks

## Inter-Agent Communication Patterns

### Request-Response
1. Agent A writes request to Agent B's inbox
2. Agent B reads from own inbox on next cycle
3. Agent B writes response to Agent A's inbox

### Broadcast
Write to `workspace/comms/broadcast.md` for system-wide announcements.

### Watcher Notification
When ticket fields change, watchers listed in the ticket are notified via their inbox.
