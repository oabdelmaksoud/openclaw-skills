#!/usr/bin/env python3
# NOTE: This file is NOT imported by langgraph_runner.py.
# langgraph_runner.py uses its own call_agent() function directly.
# This file is kept for reference/compatibility only.
"""
openclaw_llm.py — LangGraph node LLM bridge to OpenClaw gateway.

Routes all LLM calls through `openclaw agent --agent <id> --json`.
No API keys needed — uses existing OpenClaw provider configuration.
"""

import json
import subprocess
from typing import Any


def run_openclaw_agent(agent_id: str, message: str, timeout: int = 90) -> str:
    """Call openclaw agent and return text response."""
    result = subprocess.run(
        ["openclaw", "agent",
         "--agent", agent_id,
         "--message", message,
         "--json",
         "--timeout", str(timeout)],
        capture_output=True, text=True, timeout=timeout + 10,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"openclaw agent --agent {agent_id} failed (exit {result.returncode}): "
            f"{result.stderr[:200]}"
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse openclaw JSON: {e}\nOutput: {result.stdout[:300]}")

    payloads = data.get("result", {}).get("payloads", [])
    if not payloads:
        raise RuntimeError(f"No payloads in openclaw response for agent {agent_id}")
    text = payloads[0].get("text", "")
    aborted = data.get("result", {}).get("meta", {}).get("aborted", False)
    if aborted:
        raise RuntimeError(f"Agent {agent_id} turn aborted: {text[:100]}")
    return text


def extract_prompt_from_messages(messages: list | str) -> str:
    """Flatten a messages list into a single prompt string."""
    if isinstance(messages, str):
        return messages
    parts = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
        elif hasattr(msg, "role") and hasattr(msg, "content"):
            role, content = msg.role, msg.content
        else:
            role, content = "user", str(msg)
        if content:
            if role == "system":
                parts.append(f"[System Instructions]\n{content}")
            elif role == "assistant":
                parts.append(f"[Previous response]\n{content}")
            elif role == "user":
                parts.append(content)
            else:
                parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts)


class OpenClawLLM:
    """
    Plain callable LLM bridge for LangGraph nodes.
    Not tied to any LLM framework — just wraps openclaw agent CLI.
    """

    def __init__(self, agent_id: str, turn_timeout: int = 90):
        self.agent_id = agent_id
        self.turn_timeout = turn_timeout
        self.model = f"openclaw/{agent_id}"

    def call(self, messages: list | str, **kwargs) -> str:
        prompt = extract_prompt_from_messages(messages)
        return run_openclaw_agent(self.agent_id, prompt, self.turn_timeout)

    def __call__(self, messages: list | str, **kwargs) -> str:
        return self.call(messages, **kwargs)
