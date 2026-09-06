#!/usr/bin/env python3
"""CLI entrypoint for the volunteer-shift-matcher.

Loads the sample data, runs the ``shift_matcher_agent`` Strands agent, and prints
the match plan, per-volunteer confirmation messages, and the "help needed"
broadcasts for any shift that could not be fully filled.

Usage:
    python run_agent.py                 # run the full Strands agent (needs Bedrock creds)
    python run_agent.py --offline       # run only the deterministic matcher (no LLM/creds)
    python run_agent.py --shifts X --volunteers Y   # use custom data files

The problem being solved: food banks and small nonprofits chronically have
unfilled volunteer shifts because manually matching volunteer availability/skills
to open shifts is slow and error-prone for an already-stretched coordinator.
"""

from __future__ import annotations

import argparse
import json
import os
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

from shift_matcher.matching import compute_match_plan

HERE = Path(__file__).resolve().parent
DEFAULT_SHIFTS = HERE / "sample_data" / "shifts.json"
DEFAULT_VOLUNTEERS = HERE / "sample_data" / "volunteers.json"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _fmt_time(hhmm: str) -> str:
    """Render 'HH:MM' as a friendly 12-hour time, e.g. '09:00' -> '9:00am'."""
    hour, minute = (int(x) for x in hhmm.split(":"))
    suffix = "am" if hour < 12 else "pm"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d}{suffix}"


def print_match_plan(plan: dict[str, Any]) -> None:
    """Pretty-print the deterministic match plan to the console."""
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
            f"{_fmt_time(a['start_time'])}-{_fmt_time(a['end_time'])} "
            f"({a['assigned_count']}/{a['min_volunteers_needed']})"
        )
        for v in a["assigned_volunteers"]:
            print(f"         - {v['name']} <{v['email']}>")
        if a["gap"]:
            print(f"         ! GAP: {a['gap']}")
    print()


def print_messages(agent_output: dict[str, Any]) -> None:
    """Print the LLM-drafted confirmation and broadcast messages."""
    confirmations = agent_output.get("confirmation_messages", [])
    broadcasts = agent_output.get("help_needed_broadcasts", [])

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


def _extract_json(text: str) -> dict[str, Any] | None:
    """Best-effort extraction of a JSON object from the agent's text response."""
    text = text.strip()
    # Strip markdown fences if the model added them despite instructions.
    if text.startswith("```"):
        text = text.strip("`")
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def run_offline(shifts: list[dict], volunteers: list[dict]) -> dict[str, Any]:
    """Run only the deterministic matcher (no LLM). Great for demos without creds."""
    plan = compute_match_plan(shifts, volunteers)
    print_match_plan(plan)

    # Generate simple template messages so --offline still produces a full demo.
    confirmations = []
    broadcasts = []
    for a in plan["assignments"]:
        when = f"{a['date']} from {_fmt_time(a['start_time'])} to {_fmt_time(a['end_time'])}"
        for v in a["assigned_volunteers"]:
            confirmations.append(
                {
                    "shift_id": a["shift_id"],
                    "volunteer_name": v["name"],
                    "email": v["email"],
                    "message": (
                        f"Hi {v['name'].split()[0]}, thank you for volunteering! "
                        f"You're confirmed for {a['role']} on {when}. "
                        f"We're so grateful for your help -- see you then!"
                    ),
                }
            )
        if a["gap"]:
            broadcasts.append(
                {
                    "shift_id": a["shift_id"],
                    "message": (
                        f"Hi neighbors! We still {a['gap']}. "
                        f"If you can lend a hand, please reply here -- every bit helps. Thank you!"
                    ),
                }
            )

    output = {
        "match_plan": plan,
        "confirmation_messages": confirmations,
        "help_needed_broadcasts": broadcasts,
    }
    print_messages(output)
    return output


def run_with_agent(shifts: list[dict], volunteers: list[dict]) -> dict[str, Any]:
    """Run the full Strands agent: tool-based matching + LLM-drafted messages."""
    from shift_matcher.agent import build_agent

    # Silence token-by-token streaming so we can cleanly parse the final JSON.
    agent = build_agent(callback_handler=None)

    prompt = (
        "Here are the open shifts and volunteers as JSON. Call the match_shifts "
        "tool, then draft the confirmation and help-needed messages, and reply "
        "with the JSON object described in your instructions.\n\n"
        f"OPEN SHIFTS:\n{json.dumps(shifts, indent=2)}\n\n"
        f"VOLUNTEERS:\n{json.dumps(volunteers, indent=2)}"
    )

    result = agent(prompt)

    # AgentResult.message is a dict with role/content; pull out the text blocks.
    text = ""
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        for block in message.get("content", []):
            if isinstance(block, dict) and "text" in block:
                text += block["text"]
    else:
        text = str(result)

    output = _extract_json(text)
    if output is None:
        print("Could not parse structured JSON from the agent. Raw response:\n")
        print(text)
        # Fall back to the deterministic plan so the user still gets a result.
        output = {"match_plan": compute_match_plan(shifts, volunteers)}

    print("\n")
    if "match_plan" in output:
        print_match_plan(output["match_plan"])
    print_messages(output)

    print("=" * 70)
    print("STRUCTURED JSON OUTPUT")
    print("=" * 70)
    print(json.dumps(output, indent=2))
    return output


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
        run_offline(shifts, volunteers)
        return 0

    try:
        run_with_agent(shifts, volunteers)
    except Exception as exc:  # noqa: BLE001
        print(f"\nThe Strands agent could not run ({type(exc).__name__}: {exc}).")
        print("This usually means AWS Bedrock credentials are not configured.")
        print("Falling back to the deterministic offline matcher so you can still")
        print("see the match plan and template messages:\n")
        run_offline(shifts, volunteers)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
