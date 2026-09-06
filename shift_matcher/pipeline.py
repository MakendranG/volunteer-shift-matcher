"""Shared pipeline logic used by BOTH the CLI (`run_agent.py`) and the Streamlit
UI (`streamlit_app.py`), so there is a single source of truth.

Two entry points:
  - ``run_offline``: deterministic matcher + template messages (no LLM / no creds).
  - ``run_with_agent``: the full Strands agent (tool-based matching + LLM-drafted
    messages) via Amazon Bedrock.

Both return the same dict shape:
    {
      "match_plan": {...},                # from compute_match_plan / match_shifts tool
      "confirmation_messages": [...],
      "help_needed_broadcasts": [...],
      "source": "agent" | "offline",     # which path produced the messages
    }
"""

from __future__ import annotations

import json
from typing import Any

from .matching import compute_match_plan


def fmt_time(hhmm: str) -> str:
    """Render 'HH:MM' as a friendly 12-hour time, e.g. '09:00' -> '9:00am'."""
    hour, minute = (int(x) for x in hhmm.split(":"))
    suffix = "am" if hour < 12 else "pm"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d}{suffix}"


def extract_json(text: str) -> dict[str, Any] | None:
    """Best-effort extraction of a JSON object from the agent's text response."""
    text = text.strip()
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


def _template_messages(plan: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Produce simple, warm template messages without an LLM (offline mode)."""
    confirmations: list[dict] = []
    broadcasts: list[dict] = []
    for a in plan["assignments"]:
        when = f"{a['date']} from {fmt_time(a['start_time'])} to {fmt_time(a['end_time'])}"
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
                        f"Hi neighbors! We still {a['gap']}. If you can lend a hand, "
                        f"please reply here -- every bit helps. Thank you!"
                    ),
                }
            )
    return confirmations, broadcasts


def run_offline(shifts: list[dict], volunteers: list[dict]) -> dict[str, Any]:
    """Deterministic matcher + template messages. No LLM, no AWS credentials."""
    plan = compute_match_plan(shifts, volunteers)
    confirmations, broadcasts = _template_messages(plan)
    return {
        "match_plan": plan,
        "confirmation_messages": confirmations,
        "help_needed_broadcasts": broadcasts,
        "source": "offline",
    }


def _prompt_for(shifts: list[dict], volunteers: list[dict]) -> str:
    return (
        "Here are the open shifts and volunteers as JSON. Call the match_shifts "
        "tool, then draft the confirmation and help-needed messages, and reply "
        "with the JSON object described in your instructions.\n\n"
        f"OPEN SHIFTS:\n{json.dumps(shifts, indent=2)}\n\n"
        f"VOLUNTEERS:\n{json.dumps(volunteers, indent=2)}"
    )


def run_with_agent(
    shifts: list[dict],
    volunteers: list[dict],
    credentials: dict | None = None,
) -> dict[str, Any]:
    """Run the full Strands agent: tool-based matching + LLM-drafted messages.

    Args:
        shifts: open shifts.
        volunteers: volunteer pool.
        credentials: optional temporary AWS credentials (session-only) passed
            through to ``build_agent`` so a demo visitor can run the live agent on
            their own AWS account. See ``build_agent`` for accepted keys.

    Raises on any failure (missing creds, Bedrock error) so callers can decide
    whether to fall back to ``run_offline``.
    """
    # Imported lazily so offline mode never requires the SDK/credentials.
    from .agent import build_agent

    agent = build_agent(callback_handler=None, credentials=credentials)
    result = agent(_prompt_for(shifts, volunteers))

    text = ""
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        for block in message.get("content", []):
            if isinstance(block, dict) and "text" in block:
                text += block["text"]
    else:
        text = str(result)

    output = extract_json(text)
    if output is None:
        # Model didn't return parseable JSON; fall back to deterministic plan but
        # keep the raw text for transparency.
        output = {
            "match_plan": compute_match_plan(shifts, volunteers),
            "confirmation_messages": [],
            "help_needed_broadcasts": [],
            "raw_response": text,
        }
    output["source"] = "agent"
    return output
