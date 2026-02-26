#!/usr/bin/env python3
"""
crewai_runner.py — CrewAI-powered structured task runner for OpenClaw.

All LLM calls route through `openclaw agent --json` via OpenClawLLM.
No API keys needed — uses existing OpenClaw provider configuration.

Usage:
  python3 crewai_runner.py \\
    --process sequential \\
    --agents sage,pixel \\
    --tasks "Analyze|What are the 2 biggest risks in a multi-agent AI system?|A numbered list of 2 risks" \\
            "Mitigate|Propose a mitigation strategy for each risk|A numbered list of 2 mitigations" \\
    --task-id "crew-001" \\
    --output ~/.openclaw/workspace/comms/crewai/crew-001/ \\
    --turn-timeout 90 \\
    --timeout 300

Process types:
  sequential   — agents work in order, each task assigned round-robin
  hierarchical — CrewAI manager agent coordinates workers
  consensus    — sequential with consensus instruction appended to each task
"""

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
AGENTS_DIR = SKILL_DIR / "agents"

# ── venv bootstrap ────────────────────────────────────────────────────────────
_venv_lib = SKILL_DIR / ".venv" / "lib"
if _venv_lib.exists():
    for _sp in sorted(_venv_lib.glob("python3*/site-packages")):
        if str(_sp) not in sys.path:
            sys.path.insert(0, str(_sp))

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))


# ── Output helpers ────────────────────────────────────────────────────────────

def write_status(output_dir: Path, status: str, extra: dict = None):
    """Write status.json to output_dir. Always called, even on error."""
    data = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if extra:
        data.update(extra)
    (output_dir / "status.json").write_text(json.dumps(data, indent=2))


def append_transcript(output_dir: Path, text: str):
    """Append text to transcript.md (creates if missing)."""
    with open(output_dir / "transcript.md", "a", encoding="utf-8") as f:
        f.write(text + "\n")
        f.flush()


def write_result(output_dir: Path, content: str, meta: dict):
    """Write result.md with YAML-style frontmatter."""
    fm = "\n".join(f"{k}: {v}" for k, v in meta.items())
    (output_dir / "result.md").write_text(f"---\n{fm}\n---\n\n{content}\n")


# ── Agent config ──────────────────────────────────────────────────────────────

def load_agent_config(agent_id: str) -> dict:
    """Load agent JSON config from agents/ directory."""
    path = AGENTS_DIR / f"{agent_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Agent config not found: {path}. "
            f"Run: python3 {SKILL_DIR}/build_agents.py --force"
        )
    return json.loads(path.read_text())


# ── Task parsing ──────────────────────────────────────────────────────────────

def parse_task_spec(spec: str) -> dict:
    """
    Parse 'Title|Description' or 'Title|Description|Expected output'.
    At least 2 parts required; 3rd part is optional expected_output.
    """
    parts = [p.strip() for p in spec.split("|")]
    if len(parts) < 2:
        raise ValueError(
            f"Task spec must be 'Title|Description' or "
            f"'Title|Description|Expected output', got: {spec!r}"
        )
    return {
        "title":           parts[0],
        "description":     parts[1],
        "expected_output": parts[2] if len(parts) > 2 else "A clear, complete answer to the task.",
    }


# ── Crew runner ───────────────────────────────────────────────────────────────

def run_crew(args, output_dir: Path, agent_ids: list, task_specs: list) -> dict:
    """Build and run a CrewAI crew. Returns dict with result text and metadata."""
    from crewai import Agent, Task, Crew, Process
    from openclaw_llm import OpenClawLLM

    # Auto-rebuild stale agent configs (best-effort, ignore failures)
    import subprocess
    subprocess.run(
        [sys.executable, str(SKILL_DIR / "build_agents.py")],
        capture_output=True,
    )

    # ── Build CrewAI agents ───────────────────────────────────────────────────
    crewai_agents = []
    for agent_id in agent_ids:
        cfg = load_agent_config(agent_id)
        llm = OpenClawLLM(agent_id=agent_id, turn_timeout=args.turn_timeout)
        agent = Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
        crewai_agents.append(agent)
        append_transcript(
            output_dir,
            f"## Agent: {cfg['name']} ({agent_id}) — {cfg['role']}\n"
        )

    # ── Consensus instruction ─────────────────────────────────────────────────
    # 'consensus' process: sequential execution with agreement prompt appended.
    # crewai 1.9.3 only has sequential + hierarchical.
    consensus_suffix = (
        "\n\nIMPORTANT: Review all previous agents' work. "
        "If you agree with the emerging conclusion, begin your response with "
        "'CONSENSUS REACHED:' followed by the agreed answer. "
        "If you disagree, begin with 'DIVERGENT VIEW:' and explain why."
    )

    # ── Build tasks ───────────────────────────────────────────────────────────
    tasks = []
    for i, spec in enumerate(task_specs):
        assigned_agent = crewai_agents[i % len(crewai_agents)]
        desc = spec["description"]
        if args.process == "consensus":
            desc += consensus_suffix
        task = Task(
            description=desc,
            expected_output=spec["expected_output"],
            agent=assigned_agent,
        )
        tasks.append(task)
        append_transcript(
            output_dir,
            f"### Task {i+1}: {spec['title']}\n"
            f"**Agent:** {assigned_agent.role}\n"
            f"**Expected:** {spec['expected_output']}\n"
        )

    append_transcript(
        output_dir,
        f"\n## Process: {args.process}\n**Tasks:** {len(tasks)}\n\n---\n"
    )

    # ── Assemble Crew ─────────────────────────────────────────────────────────
    # crewai 1.9.3 API facts (verified):
    #   - Process.sequential and Process.hierarchical both exist
    #   - manager_llm is a valid Crew field
    #   - crew.kickoff() returns CrewOutput with .raw (str)

    effective_process = args.process  # sequential | hierarchical | consensus

    if effective_process in ("sequential", "consensus"):
        # consensus is sequential with augmented descriptions (already applied above)
        crew = Crew(
            agents=crewai_agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    elif effective_process == "hierarchical":
        # Use manager_llm pointing at 'main' (Cooper) as the orchestrator
        manager_llm = OpenClawLLM(agent_id="main", turn_timeout=args.turn_timeout)
        crew = Crew(
            agents=crewai_agents,
            tasks=tasks,
            process=Process.hierarchical,
            manager_llm=manager_llm,
            verbose=True,
        )

    else:
        # Unknown process — fall back to sequential
        crew = Crew(
            agents=crewai_agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    # ── Kick off ──────────────────────────────────────────────────────────────
    crew_result = crew.kickoff()

    # CrewOutput has .raw (str); fall back to str() for safety
    result_text = crew_result.raw if hasattr(crew_result, "raw") else str(crew_result)
    if not result_text.strip():
        result_text = "_(No output produced by crew.)_"

    append_transcript(output_dir, f"\n## Final Result\n\n{result_text}\n")

    return {
        "result":  result_text,
        "process": args.process,
        "tasks":   len(tasks),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "CrewAI structured task runner for OpenClaw.\n"
            "Routes all LLM calls through 'openclaw agent --json' — no API keys needed."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Sequential 2-agent debate\n"
            "  python3 crewai_runner.py \\\n"
            "    --process sequential \\\n"
            "    --agents sage,pixel \\\n"
            "    --tasks 'Analyze|What are 2 AI risks?|Numbered list' \\\n"
            "            'Mitigate|How to address them?|Numbered list' \\\n"
            "    --task-id crew-001 \\\n"
            "    --output /tmp/crew-001\n"
        ),
    )
    parser.add_argument(
        "--process",
        choices=["sequential", "hierarchical", "consensus"],
        default="sequential",
        help=(
            "Execution model: sequential (default), hierarchical (manager agent), "
            "consensus (sequential + agreement prompts)"
        ),
    )
    parser.add_argument(
        "--agents",
        required=True,
        help="Comma-separated agent IDs (e.g. sage,pixel,forge). Must match agents/*.json files.",
    )
    parser.add_argument(
        "--tasks",
        required=True,
        nargs="+",
        metavar="SPEC",
        help=(
            "One or more task specs in 'Title|Description|Expected output' format. "
            "Expected output is optional (defaults to generic). "
            "Tasks are assigned round-robin to agents."
        ),
    )
    parser.add_argument(
        "--task-id",
        required=True,
        dest="task_id",
        help="Unique ID for this run. Used in status.json and output directory naming.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help=(
            "Output directory path. MUST NOT already exist (race condition guard). "
            "Files written: status.json, result.md, transcript.md"
        ),
    )
    parser.add_argument(
        "--turn-timeout",
        type=int,
        default=90,
        dest="turn_timeout",
        help="Per-LLM-call timeout in seconds passed to OpenClawLLM (default: 90).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Overall crew timeout in seconds (default: 300). Not yet enforced internally.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output).expanduser().resolve()

    # ── Race condition guard ──────────────────────────────────────────────────
    if output_dir.exists():
        print(
            f"Error: output directory already exists: {output_dir}\n"
            f"Use a unique --task-id or remove the existing directory first.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except OSError as e:
        print(f"Error: could not create output directory {output_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    agent_ids  = [a.strip() for a in args.agents.split(",") if a.strip()]
    task_specs = [parse_task_spec(t) for t in args.tasks]
    started_at = time.time()

    # Write initial status immediately (before any LLM calls)
    write_status(output_dir, "running", {
        "task_id":    args.task_id,
        "process":    args.process,
        "agents":     agent_ids,
        "tasks":      len(task_specs),
        "started_at": datetime.now(timezone.utc).isoformat(),
    })

    append_transcript(
        output_dir,
        f"# CrewAI Run: {args.task_id}\n"
        f"**Started:** {datetime.now(timezone.utc).isoformat()}\n"
        f"**Process:** {args.process}\n"
        f"**Agents:** {', '.join(agent_ids)}\n\n---\n"
    )

    try:
        result   = run_crew(args, output_dir, agent_ids, task_specs)
        duration = int(time.time() - started_at)

        meta = {
            "task_id":          args.task_id,
            "process":          args.process,
            "agents":           ", ".join(agent_ids),
            "tasks":            len(task_specs),
            "duration_seconds": duration,
            "status":           "complete",
        }
        write_result(output_dir, result["result"], meta)
        write_status(output_dir, "complete", {
            "task_id":          args.task_id,
            "duration_seconds": duration,
        })

        print(f"✅ Done in {duration}s → {output_dir}")

    except Exception as e:
        duration = int(time.time() - started_at)
        tb = traceback.format_exc()
        error_content = f"**Error:** {e}\n\n```\n{tb}\n```"

        # Graceful degradation: ALWAYS write all 3 output files even on error
        write_result(output_dir, error_content, {
            "task_id":          args.task_id,
            "process":          args.process,
            "agents":           ", ".join(agent_ids),
            "tasks":            len(task_specs),
            "duration_seconds": duration,
            "status":           "error",
        })
        write_status(output_dir, "error", {
            "task_id":          args.task_id,
            "reason":           str(e),
            "duration_seconds": duration,
        })
        append_transcript(output_dir, f"\n## ERROR\n\n```\n{tb}\n```\n")

        print(f"❌ Error after {duration}s: {e}", file=sys.stderr)
        print(f"   Output: {output_dir}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
