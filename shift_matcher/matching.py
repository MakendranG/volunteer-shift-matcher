"""Deterministic shift-matching logic, exposed as a Strands custom tool.

The matching itself is pure Python so it is *deterministic and auditable*: a
coordinator (or a hackathon judge) can read exactly why each volunteer was or
was not assigned to a shift. The Strands agent calls this tool to get the hard
facts, then uses the LLM only to draft the natural-language messages.

Problem context: food banks / small nonprofits struggle to manually match
volunteer availability + skills to open shifts. This module encodes that
matching so it is fast and correct.
"""

from __future__ import annotations

from typing import Any

from strands import tool


def _to_minutes(hhmm: str) -> int:
    """Convert a 'HH:MM' 24-hour time string into minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _window_covers_shift(window: dict[str, Any], shift: dict[str, Any]) -> bool:
    """Return True if an availability window fully covers a shift's time span.

    A volunteer is only eligible if they are available for the *entire* shift on
    the *same date* -- partial time overlaps are intentionally rejected so we
    never over-promise a volunteer's time.
    """
    if window.get("date") != shift.get("date"):
        return False
    return (
        _to_minutes(window["start_time"]) <= _to_minutes(shift["start_time"])
        and _to_minutes(window["end_time"]) >= _to_minutes(shift["end_time"])
    )


def _volunteer_is_eligible(volunteer: dict[str, Any], shift: dict[str, Any]) -> bool:
    """A volunteer is eligible when they do the role AND cover the whole shift."""
    role_ok = shift["role"] in volunteer.get("roles", [])
    if not role_ok:
        return False
    return any(_window_covers_shift(w, shift) for w in volunteer.get("availability", []))


def compute_match_plan(
    shifts: list[dict[str, Any]],
    volunteers: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute a deterministic match plan for the given shifts and volunteers.

    Strategy (greedy, and deliberately simple so it stays auditable):
      1. Process shifts in chronological order (date, then start time).
      2. For each shift, assign eligible volunteers who are not already booked
         for a time-overlapping shift, up to ``min_volunteers_needed``.
      3. Prefer volunteers with fewer roles (more specialised / harder to place
         elsewhere) so generalists stay free for the shifts only they can fill.

    Returns a dict with:
      - ``assignments``: per-shift assignment detail, including a ``status`` of
        "filled", "partially_filled", or "unfilled" and a human-readable ``gap``.
      - ``summary``: counts of filled / partial / unfilled shifts.
    """
    # Track which (date) time-windows each volunteer is already committed to so a
    # single person is never double-booked for overlapping shifts.
    booked: dict[str, list[tuple[str, int, int]]] = {}

    def _has_conflict(name: str, shift: dict[str, Any]) -> bool:
        s_start, s_end = _to_minutes(shift["start_time"]), _to_minutes(shift["end_time"])
        for date, start, end in booked.get(name, []):
            if date == shift["date"] and start < s_end and s_start < end:
                return True
        return False

    ordered_shifts = sorted(
        shifts, key=lambda s: (s["date"], _to_minutes(s["start_time"]))
    )

    assignments: list[dict[str, Any]] = []

    for shift in ordered_shifts:
        eligible = [v for v in volunteers if _volunteer_is_eligible(v, shift)]
        # Specialists (fewer roles) first, then alphabetical for stable output.
        eligible.sort(key=lambda v: (len(v.get("roles", [])), v["name"]))

        assigned: list[dict[str, str]] = []
        for volunteer in eligible:
            if len(assigned) >= shift["min_volunteers_needed"]:
                break
            if _has_conflict(volunteer["name"], shift):
                continue
            assigned.append({"name": volunteer["name"], "email": volunteer["email"]})
            booked.setdefault(volunteer["name"], []).append(
                (shift["date"], _to_minutes(shift["start_time"]), _to_minutes(shift["end_time"]))
            )

        needed = shift["min_volunteers_needed"]
        filled = len(assigned)
        if filled == 0:
            status = "unfilled"
        elif filled < needed:
            status = "partially_filled"
        else:
            status = "filled"

        shortfall = max(0, needed - filled)
        gap = ""
        if shortfall > 0:
            gap = (
                f"need {shortfall} more {'person' if shortfall == 1 else 'people'} "
                f"for {shift['date']} {shift['role']}, "
                f"{shift['start_time']}-{shift['end_time']}"
            )

        assignments.append(
            {
                "shift_id": shift["shift_id"],
                "role": shift["role"],
                "date": shift["date"],
                "start_time": shift["start_time"],
                "end_time": shift["end_time"],
                "min_volunteers_needed": needed,
                "assigned_count": filled,
                "shortfall": shortfall,
                "status": status,
                "assigned_volunteers": assigned,
                "gap": gap,
            }
        )

    summary = {
        "total_shifts": len(assignments),
        "filled": sum(1 for a in assignments if a["status"] == "filled"),
        "partially_filled": sum(1 for a in assignments if a["status"] == "partially_filled"),
        "unfilled": sum(1 for a in assignments if a["status"] == "unfilled"),
    }

    return {"assignments": assignments, "summary": summary}


@tool
def match_shifts(
    shifts: list[dict[str, Any]],
    volunteers: list[dict[str, Any]],
) -> dict[str, Any]:
    """Deterministically match volunteers to open shifts and flag any gaps.

    Use this tool to compute WHO should be assigned to WHICH shift. It is pure,
    auditable Python (no LLM guessing), so the assignment plan is always correct
    and reproducible. After calling it, use the returned data to draft messages.

    Args:
        shifts: A list of open shifts. Each shift is a dict with keys:
            shift_id (str), role (str, e.g. "food sorting" / "front desk" /
            "driver"), date (str, "YYYY-MM-DD"), start_time (str, "HH:MM"),
            end_time (str, "HH:MM"), min_volunteers_needed (int).
        volunteers: A list of volunteers. Each volunteer is a dict with keys:
            name (str), email (str), roles (list[str] of roles they will do),
            availability (list of dicts each with date, start_time, end_time).

    Returns:
        A dict with two keys:
          - "assignments": a list, one entry per shift, each containing the
            assigned volunteers, the count still needed (shortfall), a status of
            "filled" / "partially_filled" / "unfilled", and a human-readable
            "gap" string for any shift that is not fully filled.
          - "summary": counts of total / filled / partially_filled / unfilled
            shifts.
    """
    return compute_match_plan(shifts, volunteers)
