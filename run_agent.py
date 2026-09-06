#!/usr/bin/env python3
"""CLI entrypoint for the volunteer-shift-matcher.

Loads the sample data, runs the ``shift_matcher_agent`` Strands agent, and prints
the match plan, per-volunteer confirmation messages, and the "help needed"
broadcasts for any shift that could not be fully filled.

Usage:
    python run_agent.py                 # run the full Strands agent (needs Bedrock creds)
    python run_agent.py --offline       # run only the deterministic matcher (no LLM/creds)
    python run_agent.py --shifts X --volunteers Y   # use custom data files

Prefer a visual UI? Run `streamlit run streamlit_app.py`.

The problem being solved: food banks and small nonprofits chronically have
unfilled volunteer shifts because manually matching volunteer availability/skills
to open shifts is slow and error-prone for an already-stretched coordinator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Load variables from a local .env file if python-dotenv is installed. This keeps
# API keys / region config out of the code and out of version control.
try:  # pragma: no cover - convenience only
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001
    pass

# All matching + agent logic lives in the shared pipeline so the CLI and the
# Streamlit UI use a single source of truth.
from shift_matcher.pipeline import fmt_time, run_offline, run_with_agent

HERE = Path(__file__).resolve().parent
DEFAULT_SHIFTS = HERE / "sample_data" / "shifts.json"
DEFAULT_VOLUNTEERS = HERE / "sample_data" / "volunteers.json"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def print_match_plan(plan: dict[str, Any]) -> None:
    """Pretty-print the match plan to the console."""
    s = plan["summary"]
    print("=" * 70)
    print("MATCH PLAN")
    print("=" * 70)
    print(
        f"{s['total_shifts']} shifts | {s['filled']} filled | "
        f"{s['partially_filled']} partially filled | {s['unfilled']} unfilled\n"
    )

    status_icon = {"filled": "[FILLED]", "partially_filled": "[PARTIAL]", "unfilled": "[UNFILLED]"}
    for a in plan["assignments"]:
        icon = status_icon.get(a["status"], "[?]")
        print(
            f"{icon} {a['shift_id']}: {a['role']} on {a['date']} "
            f"{fmt_time(a['start_time'])}-{fmt_time(a['end_time'])} "
            f"({a['assigned_count']}/{a['min_volunteers_needed']})"
        )
        for v in a["assigned_volunteers"]:
            print(f"         - {v['name']} <{v['email']}>")
        if a["gap"]:
            print(f"         ! GAP: {a['gap']}")
    print()


def print_messages(output: dict[str, Any]) -> None:
    """Print the confirmation and broadcast messages."""
    confirmations = output.get("confirmation_messages", [])
    broadcasts = output.get("help_needed_broadcasts", [])

    print("=" * 70)
    print(f"CONFIRMATION MESSAGES ({len(confirmations)})")
    print("=" * 70)
    for c in confirmations:
        print(f"To {c.get('volunteer_name')} <{c.get('email')}> [{c.get('shift_id')}]:")
        print(f"  {c.get('message')}\n")

    print("=" * 70)
    print(f"HELP-NEEDED BROADCASTS ({len(broadcasts)})")
    print("=" * 70)
    for b in broadcasts:
        print(f"[{b.get('shift_id')}] {b.get('message')}\n")


def _print_output(output: dict[str, Any], show_json: bool) -> None:
    print_match_plan(output["match_plan"])
    print_messages(output)
    if show_json:
        print("=" * 70)
        print("STRUCTURED JSON OUTPUT")
        print("=" * 70)
        print(json.dumps(output, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shifts", default=str(DEFAULT_SHIFTS), help="Path to shifts JSON.")
    parser.add_argument(
        "--volunteers", default=str(DEFAULT_VOLUNTEERS), help="Path to volunteers JSON."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run only the deterministic matcher (no LLM / no AWS credentials needed).",
    )
    args = parser.parse_args(argv)

    shifts = _load_json(Path(args.shifts))
    volunteers = _load_json(Path(args.volunteers))

    if args.offline:
        _print_output(run_offline(shifts, volunteers), show_json=False)
        return 0

    try:
        output = run_with_agent(shifts, volunteers)
    except Exception as exc:  # noqa: BLE001
        print(f"\nThe Strands agent could not run ({type(exc).__name__}: {exc}).")
        print("This usually means AWS Bedrock credentials are not configured.")
        print("Falling back to the deterministic offline matcher so you can still")
        print("see the match plan and template messages:\n")
        _print_output(run_offline(shifts, volunteers), show_json=False)
        return 0

    print()
    _print_output(output, show_json=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
