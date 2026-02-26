#!/usr/bin/env python3
"""
langgraph_runner.py — Stateful multi-agent graph runner using LangGraph.

Topologies: linear, supervisor, parallel, conditional
Routes all LLM calls through `openclaw agent --agent <id> --json`.
No API keys needed — uses existing OpenClaw provider configuration.

Usage:
  python3 langgraph_runner.py \\
    --topology linear \\
    --agents sage,pixel \\
    --task "What makes a distributed system reliable?" \\
    --task-id smoke-001 \\
    --output /path/to/output/dir/ \\
    --max-steps 5 \\
    --turn-timeout 90 \\
    --timeout 300
"""

import argparse
import json
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, List, TypedDict

import operator

# LangGraph imports
from langgraph.graph import END, StateGraph

SKILL_DIR = Path(__file__).parent
AGENTS_DIR = SKILL_DIR / "agents"


# ─────────────────────────────────────────────────────────────────────────────
# State definition
# ─────────────────────────────────────────────────────────────────────────────

class GraphState(TypedDict):
    task: str
    messages: Annotated[List[dict], operator.add]   # accumulates across all nodes
    metadata: dict
    result: str
    steps: int
    next_agent: str      # used by supervisor routing


# ─────────────────────────────────────────────────────────────────────────────
# Output manager
# ─────────────────────────────────────────────────────────────────────────────

class OutputManager:
    def __init__(self, output_dir: Path, task_id: str):
        self.output_dir = output_dir
        self.task_id = task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        self._transcript_path = output_dir / "transcript.md"
        self._status_path = output_dir / "status.json"
        self._result_path = output_dir / "result.md"
        # Initialise files
        self._transcript_path.write_text(f"# Transcript — {task_id}\n\n")
        self._write_status("running", "")

    # ── transcript ──────────────────────────────────────────────────────────

    def log(self, agent_id: str, content: str, node_type: str = "agent") -> None:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"## [{ts}] {agent_id.upper()} ({node_type})\n\n{content}\n\n---\n\n"
        with open(self._transcript_path, "a") as fh:
            fh.write(entry)
        preview = content[:80].replace("\n", " ")
        print(f"[{ts}] [{agent_id}] {preview}...", file=sys.stderr, flush=True)

    # ── status ───────────────────────────────────────────────────────────────

    def _write_status(self, status: str, message: str, extra: dict | None = None) -> None:
        data: dict = {
            "task_id": self.task_id,
            "status": status,
            "message": message,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if extra:
            data.update(extra)
        self._status_path.write_text(json.dumps(data, indent=2))

    def complete(self, result: str, steps: int) -> None:
        self._write_status("complete", f"Completed in {steps} steps", {"steps": steps})
        fm = (
            f"---\n"
            f"task_id: {self.task_id}\n"
            f"status: complete\n"
            f"steps: {steps}\n"
            f"timestamp: {datetime.now(timezone.utc).isoformat()}\n"
            f"---\n\n"
        )
        self._result_path.write_text(fm + result)

    def error(self, exc: Exception, steps: int, tb_str: str = "") -> None:
        msg = str(exc)[:400]
        self._write_status("error", msg, {"steps": steps})
        fm = (
            f"---\n"
            f"task_id: {self.task_id}\n"
            f"status: error\n"
            f"steps: {steps}\n"
            f"timestamp: {datetime.now(timezone.utc).isoformat()}\n"
            f"---\n\n"
        )
        self._result_path.write_text(fm + f"ERROR: {msg}\n\n```\n{tb_str or msg}\n```\n")


# ─────────────────────────────────────────────────────────────────────────────
# OpenClaw agent caller
# ─────────────────────────────────────────────────────────────────────────────

def load_agent_config(agent_id: str) -> dict:
    config_path = AGENTS_DIR / f"{agent_id}.json"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Agent config not found: {config_path}\n"
            f"Run: python3 {SKILL_DIR}/build_agents.py --force"
        )
    return json.loads(config_path.read_text())


def call_agent(agent_id: str, prompt: str, turn_timeout: int = 90) -> str:
    """Invoke `openclaw agent --json` and return the text response."""
    result = subprocess.run(
        [
            "openclaw", "agent",
            "--agent", agent_id,
            "--message", prompt,
            "--json",
            "--timeout", str(turn_timeout),
        ],
        capture_output=True,
        text=True,
        timeout=turn_timeout + 20,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"openclaw agent --agent {agent_id} failed "
            f"(exit {result.returncode}): {result.stderr[:400]}"
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Failed to parse JSON from openclaw agent {agent_id}: {exc}\n"
            f"Raw output: {result.stdout[:500]}"
        ) from exc

    payloads = data.get("result", {}).get("payloads", [])
    if not payloads:
        raise RuntimeError(f"No payloads in openclaw response for agent {agent_id}")

    text = payloads[0].get("text", "")
    aborted = data.get("result", {}).get("meta", {}).get("aborted", False)
    if aborted:
        raise RuntimeError(f"Agent {agent_id} turn was aborted by runtime")
    return text


# ─────────────────────────────────────────────────────────────────────────────
# Node factories
# ─────────────────────────────────────────────────────────────────────────────

def make_worker_node(agent_id: str, out: OutputManager, turn_timeout: int):
    """Return a LangGraph node function for a standard worker agent."""
    config = load_agent_config(agent_id)
    role = config.get("role", agent_id)
    name = config.get("name", agent_id)
    goal = config.get("goal", "")

    def _node(state: GraphState) -> dict:
        task = state["task"]
        prior = state.get("messages", [])
        steps = state.get("steps", 0)

        # Build context from recent messages (capped to avoid token blow-up)
        ctx_parts = [
            f"[{m['agent'].upper()} — {m['role']}]:\n{m['content']}"
            for m in prior[-6:]
        ]
        ctx = "\n\n".join(ctx_parts) if ctx_parts else "No prior context."

        prompt = (
            f"You are {name}, {role}.\n"
            f"Goal: {goal}\n\n"
            f"## Task\n{task}\n\n"
            f"## Prior Work\n{ctx}\n\n"
            f"## Your Turn\n"
            f"Contribute your expertise. Be specific and concise."
        )

        response = call_agent(agent_id, prompt, turn_timeout)
        out.log(agent_id, response, "worker")

        # Parse METADATA: key=value lines from agent response
        new_metadata = dict(state.get("metadata", {}))
        for line in response.splitlines():
            line = line.strip()
            if line.upper().startswith("METADATA:"):
                kv = line.split(":", 1)[1].strip()
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    new_metadata[k.strip()] = v.strip()

        return {
            "messages": [{"agent": agent_id, "role": role, "content": response}],
            "steps": steps + 1,
            "result": response,
            "metadata": new_metadata,
        }

    _node.__name__ = f"node_{agent_id}"
    return _node


def make_supervisor_node(
    supervisor_id: str,
    worker_ids: list[str],
    out: OutputManager,
    turn_timeout: int,
):
    """Return a supervisor node that decides which worker runs next or FINISH."""
    config = load_agent_config(supervisor_id)
    name = config.get("name", supervisor_id)
    workers_str = ", ".join(worker_ids)

    def _node(state: GraphState) -> dict:
        task = state["task"]
        prior = state.get("messages", [])
        steps = state.get("steps", 0)

        ctx_parts = [
            f"[{m['agent'].upper()} — {m['role']}]:\n{m['content'][:400]}"
            for m in prior
        ]
        ctx = "\n\n".join(ctx_parts) if ctx_parts else "No work done yet."

        prompt = (
            f"You are {name}, the orchestrating supervisor for this task.\n\n"
            f"## Task\n{task}\n\n"
            f"## Work Done So Far\n{ctx}\n\n"
            f"## Available Workers\n{workers_str}\n\n"
            f"## Instructions\n"
            f"Decide who should work next, or whether the task is complete enough.\n"
            f"- To delegate: respond with exactly `NEXT: <worker_id>` on its own line "
            f"(one of: {workers_str})\n"
            f"- To finish: respond with exactly `NEXT: FINISH` on its own line\n\n"
            f"Also provide a brief explanation. Your response MUST contain a "
            f"`NEXT: <id>` or `NEXT: FINISH` line."
        )

        response = call_agent(supervisor_id, prompt, turn_timeout)
        out.log(supervisor_id, response, "supervisor")

        # Parse NEXT: directive
        m = re.search(r"NEXT:\s*(\S+)", response, re.IGNORECASE)
        next_agent = "FINISH"
        if m:
            candidate = m.group(1).strip().rstrip(".,;").lower()
            if candidate == "finish":
                next_agent = "FINISH"
            elif candidate in worker_ids:
                next_agent = candidate
            # else: unknown → treat as FINISH

        return {
            "messages": [{"agent": supervisor_id, "role": "supervisor", "content": response}],
            "steps": steps + 1,
            "next_agent": next_agent,
        }

    _node.__name__ = f"node_{supervisor_id}_supervisor"
    return _node


def make_synthesizer_node(synthesizer_id: str, out: OutputManager, turn_timeout: int):
    """Return a synthesizer node that combines all prior worker outputs."""
    config = load_agent_config(synthesizer_id)
    name = config.get("name", synthesizer_id)
    role = config.get("role", synthesizer_id)
    goal = config.get("goal", "")

    def _node(state: GraphState) -> dict:
        task = state["task"]
        prior = state.get("messages", [])
        steps = state.get("steps", 0)

        sections = [
            f"### {m['agent'].upper()} ({m['role']})\n{m['content']}"
            for m in prior
        ]
        perspectives = "\n\n".join(sections) if sections else "No expert input."

        prompt = (
            f"You are {name}, {role}.\n"
            f"Goal: {goal}\n\n"
            f"## Original Task\n{task}\n\n"
            f"## Expert Perspectives\n{perspectives}\n\n"
            f"## Your Role\n"
            f"Synthesise all perspectives into a single, cohesive, actionable response. "
            f"Note consensus, flag disagreements, and deliver a unified recommendation."
        )

        response = call_agent(synthesizer_id, prompt, turn_timeout)
        out.log(synthesizer_id, response, "synthesizer")

        return {
            "messages": [{"agent": synthesizer_id, "role": "synthesizer", "content": response}],
            "steps": steps + 1,
            "result": response,
        }

    _node.__name__ = f"node_{synthesizer_id}_synth"
    return _node


# ─────────────────────────────────────────────────────────────────────────────
# Graph builders
# ─────────────────────────────────────────────────────────────────────────────

def build_linear_graph(agents: list[str], out: OutputManager, turn_timeout: int):
    """A → B → C → END (sequential pipeline, each output feeds the next)."""
    g = StateGraph(GraphState)
    for aid in agents:
        g.add_node(aid, make_worker_node(aid, out, turn_timeout))
    g.set_entry_point(agents[0])
    for i in range(len(agents) - 1):
        g.add_edge(agents[i], agents[i + 1])
    g.add_edge(agents[-1], END)
    return g.compile()


def build_supervisor_graph(
    agents: list[str],
    supervisor_id: str,
    max_steps: int,
    out: OutputManager,
    turn_timeout: int,
):
    """Supervisor ⇄ workers (dynamic routing until FINISH or max_steps)."""
    g = StateGraph(GraphState)

    # Worker nodes
    for aid in agents:
        g.add_node(aid, make_worker_node(aid, out, turn_timeout))

    # Supervisor node
    g.add_node("supervisor", make_supervisor_node(supervisor_id, agents, out, turn_timeout))

    # Entry → supervisor
    g.set_entry_point("supervisor")

    # Workers always return to supervisor
    for aid in agents:
        g.add_edge(aid, "supervisor")

    # Supervisor routes to worker or END
    def route(state: GraphState) -> str:
        agent_ids = agents  # local alias for clarity in condition
        nxt = state.get("next_agent", "FINISH")
        steps = state.get("steps", 0)
        if steps >= max_steps or nxt == "FINISH" or nxt not in agent_ids:
            return END
        return nxt

    cond_map = {aid: aid for aid in agents}
    cond_map[END] = END
    g.add_conditional_edges("supervisor", route, cond_map)

    return g.compile()


def build_parallel_graph(
    agents: list[str],
    synthesizer_id: str,
    out: OutputManager,
    turn_timeout: int,
):
    """All workers → synthesizer → END (fan-out with synthesis).

    Note: LangGraph v0.6 doesn't natively fan-out with true concurrency here;
    we chain workers sequentially so every perspective is gathered, then
    synthesise — which is semantically equivalent for our use-case.
    """
    g = StateGraph(GraphState)

    for aid in agents:
        g.add_node(aid, make_worker_node(aid, out, turn_timeout))
    g.add_node("synthesizer", make_synthesizer_node(synthesizer_id, out, turn_timeout))

    g.set_entry_point(agents[0])
    for i in range(len(agents) - 1):
        g.add_edge(agents[i], agents[i + 1])
    g.add_edge(agents[-1], "synthesizer")
    g.add_edge("synthesizer", END)

    return g.compile()


def build_conditional_graph(
    agents: list[str],
    condition_str: str,
    out: OutputManager,
    turn_timeout: int,
):
    """Initial agent → condition check → branch A or B → END."""
    m = re.match(r"(\w+)=(\w+):(\w+),(\w+)", condition_str)
    if not m:
        raise ValueError(
            f"Invalid --condition format: '{condition_str}'\n"
            f"Expected: key=value:agent_true,agent_false"
        )
    cond_key, cond_value, agent_true, agent_false = m.groups()

    initial_agent = agents[0]
    all_agents = list(dict.fromkeys([initial_agent, agent_true, agent_false]))

    g = StateGraph(GraphState)
    for aid in all_agents:
        g.add_node(aid, make_worker_node(aid, out, turn_timeout))

    g.set_entry_point(initial_agent)

    def _condition(state: GraphState) -> str:
        return agent_true if state.get("metadata", {}).get(cond_key) == cond_value else agent_false

    # Initial agent routes to one of the two branches
    if initial_agent != agent_true and initial_agent != agent_false:
        g.add_conditional_edges(
            initial_agent,
            _condition,
            {agent_true: agent_true, agent_false: agent_false},
        )
    else:
        # If initial is one of the branches, just go to the other
        g.add_edge(initial_agent, agent_false if initial_agent == agent_true else agent_true)

    g.add_edge(agent_true, END)
    g.add_edge(agent_false, END)

    return g.compile()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LangGraph multi-agent runner (OpenClaw gateway routing)"
    )
    parser.add_argument(
        "--topology", required=True,
        choices=["linear", "supervisor", "parallel", "conditional"],
    )
    parser.add_argument("--agents", required=True, help="Comma-separated agent IDs")
    parser.add_argument("--supervisor", default="main",
                        help="Supervisor/synthesizer agent ID (default: main)")
    parser.add_argument("--synthesizer", default=None,
                        help="Override synthesizer for parallel topology")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--task-id", required=True, help="Unique task ID")
    parser.add_argument("--output", required=True, help="Output directory path")
    parser.add_argument("--max-steps", type=int, default=10,
                        help="Max graph steps / recursion limit guard (default: 10)")
    parser.add_argument("--turn-timeout", type=int, default=90,
                        help="Per-agent turn timeout in seconds (default: 90)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Total run timeout in seconds (default: 300)")
    parser.add_argument("--condition", default=None,
                        help="Condition for conditional topology: key=value:agent_true,agent_false")
    parser.add_argument("--metadata", default="{}",
                        help="Initial metadata JSON string")
    args = parser.parse_args()

    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    if args.topology == "conditional" and not args.condition:
        print("Error: --condition is required for conditional topology.\n"
              "Format: 'key=value:agent_true,agent_false'\n"
              "Example: 'bug_found=true:forge,vigil'", file=sys.stderr)
        sys.exit(1)
    output_dir = Path(args.output)
    try:
        out = OutputManager(output_dir, args.task_id)
    # Cannot write output files here — directory creation failed, no output dir to write to.
    except OSError as e:
        print(f"Error: could not create output directory {output_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError:
        metadata = {}

    initial_state: GraphState = {
        "task": args.task,
        "messages": [],
        "metadata": metadata,
        "result": "",
        "steps": 0,
        "next_agent": "",
    }

    print(
        f"[langgraph-runner] topology={args.topology} "
        f"agents={agents} task_id={args.task_id}",
        file=sys.stderr, flush=True,
    )

    start = time.time()
    steps_done = 0

    try:
        # ── Build graph ──────────────────────────────────────────────────────
        if args.topology == "linear":
            compiled = build_linear_graph(agents, out, args.turn_timeout)

        elif args.topology == "supervisor":
            compiled = build_supervisor_graph(
                agents, args.supervisor, args.max_steps, out, args.turn_timeout
            )

        elif args.topology == "parallel":
            synth_id = args.synthesizer or args.supervisor
            compiled = build_parallel_graph(agents, synth_id, out, args.turn_timeout)

        elif args.topology == "conditional":
            if not args.condition:
                raise ValueError("--condition is required for conditional topology")
            compiled = build_conditional_graph(
                agents, args.condition, out, args.turn_timeout
            )

        else:
            raise ValueError(f"Unknown topology: {args.topology}")

        # ── Run ──────────────────────────────────────────────────────────────
        final_state = compiled.invoke(
            initial_state,
            {"recursion_limit": args.max_steps + 5},
        )

        elapsed = time.time() - start
        steps_done = final_state.get("steps", 0)
        result = final_state.get("result", "")

        # Fall back to last message content if result field is empty
        if not result and final_state.get("messages"):
            result = final_state["messages"][-1].get("content", "")

        print(
            f"[langgraph-runner] Complete in {elapsed:.1f}s | steps={steps_done}",
            file=sys.stderr, flush=True,
        )
        out.complete(result, steps_done)

    except Exception as exc:
        elapsed = time.time() - start
        tb_str = traceback.format_exc()
        print(
            f"[langgraph-runner] ERROR after {elapsed:.1f}s: {exc}",
            file=sys.stderr, flush=True,
        )
        out.error(exc, steps_done, tb_str)
        sys.exit(1)


if __name__ == "__main__":
    main()
