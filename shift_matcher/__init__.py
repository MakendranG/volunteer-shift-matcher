"""volunteer-shift-matcher

A Strands Agents SDK project that helps volunteer coordinators at food banks and
small nonprofits fill open volunteer shifts.

Problem statement
-----------------
Food banks and small nonprofits chronically have unfilled volunteer shifts --
not because volunteers don't exist, but because manually matching volunteer
availability/skills to open shifts (via spreadsheets or group texts) is slow and
error-prone for a coordinator who is already stretched thin.

This package exposes:
- ``match_shifts``: a deterministic, auditable Strands @tool that computes the
  match plan in pure Python.
- ``build_agent``: constructs the ``shift_matcher_agent`` Strands agent that
  calls the tool and uses the LLM to draft warm, natural-language messages.
"""

from .matching import match_shifts, compute_match_plan
from .agent import build_agent, SYSTEM_PROMPT
from .pipeline import run_offline, run_with_agent

__all__ = [
    "match_shifts",
    "compute_match_plan",
    "build_agent",
    "SYSTEM_PROMPT",
    "run_offline",
    "run_with_agent",
]
