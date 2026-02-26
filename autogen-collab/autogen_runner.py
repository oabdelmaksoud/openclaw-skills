#!/usr/bin/env python3
"""
autogen_runner.py — AutoGen-style debate runner using OpenClaw's gateway.

Each agent turn is run via `openclaw agent --agent <id> --json`, so all
provider credentials are handled by OpenClaw — no API keys needed here.

Usage:
  python3 autogen_runner.py \
    --mode debate \
    --agents sage,pixel \
    --task "Design the trading engine architecture" \
    --task-id "abc-123" \
    --output /path/to/workspace/comms/autogen/abc-123/ \
    --max-rounds 10 \
    --timeout 300

Output (always written, even on failure):
  <output>/status.json    — run status: running / complete / timeout / error
  <output>/result.md      — final answer with YAML frontmatter
  <output>/transcript.md  — full conversation, flushed per turn
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILL_DIR = Path(__file__).resolve().parent
CONSENSUS_SIGNAL = "##AGREED##"
MAX_HISTORY_TURNS = 6  # prevent context window overflow on long debates


# ── Output helpers ────────────────────────────────────────────────────────────

def write_status(output_dir: Path, status: str, extra: dict = None):
    data = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if extra:
        data.update(extra)
    (output_dir / "status.json").write_text(json.dumps(data, indent=2))


def append_transcript(output_dir: Path, text: str):
    with open(output_dir / "transcript.md", "a", encoding="utf-8") as f:
        f.write(text + "\n")
        f.flush()


def write_result(output_dir: Path, content: str, meta: dict):
    frontmatter = "\n".join(f"{k}: {v}" for k, v in meta.items())
    (output_dir / "result.md").write_text(f"---\n{frontmatter}\n---\n\n{content}\n")


def synthesize_transcript(output_dir: Path) -> str:
    path = output_dir / "transcript.md"
    if not path.exists():
        return "No transcript available."
    lines = path.read_text().splitlines()
    tail = "\n".join(lines[-40:]) if len(lines) > 40 else "\n".join(lines)
    return f"**Note: Consensus not reached within limits.**\n\nFinal discussion:\n\n{tail}"


# ── OpenClaw agent call ───────────────────────────────────────────────────────

def run_agent_turn(agent_id: str, message: str, timeout: int = 120) -> str:
    """
    Call `openclaw agent --agent <id> --message <msg> --json` and return
    the agent's text response. Raises on failure.
    """
    result = subprocess.run(
        [
            "openclaw", "agent",
            "--agent", agent_id,
            "--message", message,
            "--json",
            "--timeout", str(timeout),
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 10,
    )

    if result.returncode != 0:
        raise RuntimeError(f"openclaw agent exited {result.returncode}: {result.stderr[:200]}")

    try:
        data = json.loads(result.stdout)
        payloads = data.get("result", {}).get("payloads", [])
        if not payloads:
            raise ValueError("No payloads in response")
        text = payloads[0].get("text", "")
        aborted = data.get("result", {}).get("meta", {}).get("aborted", False)
        if aborted:
            raise RuntimeError(f"Agent turn aborted (timeout or error): {text[:100]}")
        return text
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse agent JSON response: {e}\nOutput: {result.stdout[:200]}")


# ── Debate loop ───────────────────────────────────────────────────────────────

def build_context(task: str, history: list[dict]) -> str:
    """
    Build the full conversation context to pass to the next agent.
    Each agent gets: original task + full conversation history so far.
    """
    lines = [
        f"## Debate Task\n\n{task}\n",
        "## Conversation So Far\n",
    ]
    recent_history = history[-MAX_HISTORY_TURNS:] if len(history) > MAX_HISTORY_TURNS else history
    if not recent_history:
        lines.append("_(You are the first to respond.)_\n")
    else:
        for turn in recent_history:
            lines.append(f"**{turn['agent']}:** {turn['response']}\n")

    lines.append(
        f"\n## Your Turn\n\n"
        f"Respond concisely. If you genuinely agree with the last response, "
        f"write `{CONSENSUS_SIGNAL}` alone on a new line at the end of your message."
    )
    return "\n".join(lines)


def run_debate(args, output_dir: Path, agent_ids: list[str]) -> dict:
    task = args.task
    history = []
    consensus_reached = False
    rounds = 0
    final_message = ""
    deadline = time.time() + args.timeout

    append_transcript(output_dir, f"# Debate · {args.task_id}\n\n**Task:** {task}\n\n**Agents:** {', '.join(agent_ids)}\n\n---\n")

    # Round-robin until consensus, max_rounds, or timeout
    agent_cycle = list(agent_ids)
    cycle_idx = 0

    while rounds < args.max_rounds:
        if time.time() > deadline:
            break

        agent_id = agent_cycle[cycle_idx % len(agent_cycle)]
        cycle_idx += 1

        context = build_context(task, history)
        remaining_timeout = max(10, int(deadline - time.time()))
        per_turn_timeout = min(remaining_timeout, args.turn_timeout)

        append_transcript(output_dir, f"\n### Round {rounds + 1} · {agent_id}\n")

        try:
            response = run_agent_turn(agent_id, context, timeout=per_turn_timeout)
        except Exception as e:
            append_transcript(output_dir, f"_[{agent_id} error: {e}]_\n")
            rounds += 1
            continue

        append_transcript(output_dir, f"{response}\n")
        history.append({"agent": agent_id, "response": response})
        final_message = response
        rounds += 1

        # Update running status
        write_status(output_dir, "running", {
            "task_id": args.task_id,
            "rounds_completed": rounds,
        })

        if any(line.strip() == CONSENSUS_SIGNAL for line in response.splitlines()):
            consensus_reached = True
            break

    return {
        "rounds": rounds,
        "consensus_reached": consensus_reached,
        "final_message": final_message,
        "history": history,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="OpenClaw multi-agent debate runner")
    parser.add_argument("--mode", choices=["debate"], default="debate")
    parser.add_argument("--agents", required=True, help="Comma-separated agent IDs")
    parser.add_argument("--task", required=True, help="Task/question for debate")
    parser.add_argument("--task-id", required=True, dest="task_id")
    parser.add_argument("--output", required=True, help="Output directory path")
    parser.add_argument("--max-rounds", type=int, default=10, dest="max_rounds")
    parser.add_argument("--timeout", type=int, default=300, help="Total wall-clock timeout (seconds)")
    parser.add_argument("--turn-timeout", type=int, default=60, dest="turn_timeout",
                        help="Per-turn timeout (seconds)")
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output)

    # Race condition prevention
    if output_dir.exists():
        print(f"Error: output directory already exists: {output_dir}", file=sys.stderr)
        sys.exit(1)
    output_dir.mkdir(parents=True, exist_ok=False)

    agent_ids = [a.strip() for a in args.agents.split(",") if a.strip()]
    started_at = time.time()

    # Write initial status immediately
    write_status(output_dir, "running", {
        "task_id": args.task_id,
        "agents": agent_ids,
        "started_at": datetime.now(timezone.utc).isoformat(),
    })

    try:
        result = run_debate(args, output_dir, agent_ids)
        duration = int(time.time() - started_at)

        meta = {
            "task_id": args.task_id,
            "mode": args.mode,
            "agents": ", ".join(agent_ids),
            "rounds": result["rounds"],
            "consensus_reached": str(result["consensus_reached"]).lower(),
            "duration_seconds": duration,
        }

        timed_out = (not result["consensus_reached"]
                     and result["rounds"] >= args.max_rounds
                     or time.time() - started_at >= args.timeout)

        if result["consensus_reached"]:
            write_result(output_dir, result["final_message"], meta)
            write_status(output_dir, "complete", {
                "task_id": args.task_id,
                "consensus_reached": True,
                "rounds": result["rounds"],
                "duration_seconds": duration,
            })
        elif timed_out:
            write_result(output_dir, synthesize_transcript(output_dir), meta)
            write_status(output_dir, "timeout", {
                "task_id": args.task_id,
                "reason": "Max rounds or wall-clock timeout reached without consensus",
                "rounds": result["rounds"],
                "duration_seconds": duration,
            })
        else:
            write_result(output_dir, synthesize_transcript(output_dir), meta)
            write_status(output_dir, "complete", {
                "task_id": args.task_id,
                "consensus_reached": False,
                "rounds": result["rounds"],
                "duration_seconds": duration,
            })

    except Exception as e:
        import traceback
        duration = int(time.time() - started_at)
        tb = traceback.format_exc()
        write_result(output_dir, f"**Error:** {e}\n\n```\n{tb}\n```", {
            "task_id": args.task_id,
            "mode": args.mode,
            "agents": ", ".join(agent_ids),
            "rounds": 0,
            "consensus_reached": "false",
            "duration_seconds": duration,
        })
        write_status(output_dir, "error", {
            "task_id": args.task_id,
            "reason": str(e),
            "duration_seconds": duration,
        })
        sys.exit(1)


if __name__ == "__main__":
    main()
