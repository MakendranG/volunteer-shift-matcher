"""Tests for the deterministic matching logic.

These tests do NOT require an LLM or AWS credentials -- they exercise the pure
Python matching that powers the `match_shifts` Strands tool, so the assignment
logic stays auditable and regression-safe.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from shift_matcher.matching import (
    compute_match_plan,
    match_shifts,
    _to_minutes,
    _window_covers_shift,
    _volunteer_is_eligible,
)

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture
def sample_shifts() -> list[dict]:
    return json.loads((SAMPLE_DIR / "shifts.json").read_text())


@pytest.fixture
def sample_volunteers() -> list[dict]:
    return json.loads((SAMPLE_DIR / "volunteers.json").read_text())


def test_to_minutes():
    assert _to_minutes("00:00") == 0
    assert _to_minutes("09:30") == 570
    assert _to_minutes("23:59") == 1439


def test_window_covers_shift_true():
    window = {"date": "2026-09-12", "start_time": "08:00", "end_time": "12:30"}
    shift = {"date": "2026-09-12", "start_time": "09:00", "end_time": "12:00"}
    assert _window_covers_shift(window, shift) is True


def test_window_rejects_wrong_date():
    window = {"date": "2026-09-13", "start_time": "08:00", "end_time": "13:00"}
    shift = {"date": "2026-09-12", "start_time": "09:00", "end_time": "12:00"}
    assert _window_covers_shift(window, shift) is False


def test_window_rejects_partial_coverage():
    # Window ends before the shift ends -> not eligible.
    window = {"date": "2026-09-12", "start_time": "09:00", "end_time": "11:00"}
    shift = {"date": "2026-09-12", "start_time": "09:00", "end_time": "12:00"}
    assert _window_covers_shift(window, shift) is False


def test_eligibility_requires_matching_role():
    volunteer = {
        "name": "Test",
        "roles": ["driver"],
        "availability": [{"date": "2026-09-12", "start_time": "08:00", "end_time": "17:00"}],
    }
    shift = {"role": "food sorting", "date": "2026-09-12", "start_time": "09:00", "end_time": "12:00"}
    assert _volunteer_is_eligible(volunteer, shift) is False


def test_sample_data_produces_expected_gap(sample_shifts, sample_volunteers):
    """The sample data is engineered so S3 (Sat driver, needs 2) is only partially
    filled -- this proves the agent handles a realistic imperfect scenario."""
    plan = compute_match_plan(sample_shifts, sample_volunteers)
    by_id = {a["shift_id"]: a for a in plan["assignments"]}

    assert by_id["S3"]["status"] == "partially_filled"
    assert by_id["S3"]["assigned_count"] == 1
    assert by_id["S3"]["shortfall"] == 1
    assert "need 1 more person" in by_id["S3"]["gap"]

    # And at least one shift should be fully filled to prove matching works.
    assert plan["summary"]["filled"] >= 1
    assert plan["summary"]["total_shifts"] == len(sample_shifts)


def test_no_double_booking(sample_shifts, sample_volunteers):
    """No volunteer should be assigned to two time-overlapping shifts."""
    plan = compute_match_plan(sample_shifts, sample_volunteers)
    seen: dict[str, list[tuple[str, str, str]]] = {}
    for a in plan["assignments"]:
        for v in a["assigned_volunteers"]:
            for (date, start, end) in seen.get(v["name"], []):
                if date == a["date"]:
                    # No overlap allowed.
                    assert not (start < a["end_time"] and a["start_time"] < end)
            seen.setdefault(v["name"], []).append((a["date"], a["start_time"], a["end_time"]))


def test_unfilled_shift_flagged():
    """A shift with no eligible volunteers is flagged 'unfilled' with a gap."""
    shifts = [
        {
            "shift_id": "X1",
            "role": "driver",
            "date": "2026-09-12",
            "start_time": "09:00",
            "end_time": "12:00",
            "min_volunteers_needed": 2,
        }
    ]
    volunteers = [
        {
            "name": "Only Sorter",
            "email": "sorter@example.com",
            "roles": ["food sorting"],
            "availability": [{"date": "2026-09-12", "start_time": "08:00", "end_time": "17:00"}],
        }
    ]
    plan = compute_match_plan(shifts, volunteers)
    a = plan["assignments"][0]
    assert a["status"] == "unfilled"
    assert a["assigned_count"] == 0
    assert a["shortfall"] == 2
    assert a["gap"] != ""


def test_match_shifts_tool_callable(sample_shifts, sample_volunteers):
    """The @tool-decorated function should still be directly callable and return
    the same structure as compute_match_plan."""
    # Strands wraps the function; the underlying callable is available for tests.
    fn = getattr(match_shifts, "_tool_func", None) or getattr(
        match_shifts, "__wrapped__", match_shifts
    )
    result = fn(sample_shifts, sample_volunteers)
    assert "assignments" in result
    assert "summary" in result
    assert result["summary"]["total_shifts"] == len(sample_shifts)
