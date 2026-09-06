"""The ``shift_matcher_agent`` Strands agent.

This is a genuine Strands implementation, not a single raw LLM prompt:
  - It registers a deterministic custom @tool (``match_shifts``) that performs
    the actual matching in Python, so assignments are auditable.
  - The agent (LLM) is responsible for orchestration + drafting the warm,
    human-readable confirmation and "help needed" broadcast messages.

Model configuration is read entirely from environment variables -- there are no
hardcoded API keys or credentials anywhere in this file.
"""

from __future__ import annotations

import os

from strands import Agent
from strands.models import BedrockModel

from .matching import match_shifts

# System prompt framing the agent as a helpful volunteer coordinator assistant.
SYSTEM_PROMPT = """\
You are shift_matcher_agent, an assistant for volunteer coordinators at food banks
and small nonprofits. These coordinators are stretched thin and lose time manually
matching volunteers to open shifts with spreadsheets and group texts.

Your job, given a list of OPEN SHIFTS and a list of VOLUNTEERS:

1. ALWAYS call the `match_shifts` tool to compute the assignment plan. Never guess
   the assignments yourself -- the tool is the single source of truth. Pass the
   shifts and volunteers through to it unchanged.

2. Using the tool's result, draft messages:
   - For every assigned volunteer: a short, warm confirmation message written as if
     from the coordinator, mentioning the shift role, date, and start-end time.
   - For every shift with status "partially_filled" or "unfilled": a short,
     friendly "help needed" broadcast suitable for a group text or newsletter,
     describing the specific gap (use the tool's `gap` text, e.g. "need 2 more
     people for Saturday food sorting, 9am-12pm").

3. Respond with a single valid JSON object ONLY (no markdown fences, no prose
   before or after) with EXACTLY this shape:
   {
     "match_plan": <the exact object returned by the match_shifts tool>,
     "confirmation_messages": [
       {"shift_id": "...", "volunteer_name": "...", "email": "...", "message": "..."}
     ],
     "help_needed_broadcasts": [
       {"shift_id": "...", "message": "..."}
     ]
   }

Keep messages warm, concise, and specific. Do not invent volunteers, shifts, or
contact details beyond what the tool returns.
"""


def build_agent(callback_handler: object = "__default__") -> Agent:
    """Construct and return the ``shift_matcher_agent`` Strands agent.

    Model selection is driven purely by environment variables so no secrets are
    baked into the code:
      - ``BEDROCK_MODEL_ID``  (optional) overrides the Bedrock model id.
      - ``AWS_REGION`` / ``AWS_DEFAULT_REGION`` (optional) selects the region.
      - AWS credentials are picked up by boto3 from the standard environment
        (env vars, shared credentials file, or IAM role).

    Args:
        callback_handler: Passed through to ``Agent``. Leave as the default to
            stream the agent's reasoning to the console, or pass ``None`` to
            silence streaming (useful when you only want the final JSON).

    Returns:
        A configured :class:`strands.Agent` with the ``match_shifts`` tool.
    """
    model_id = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-west-2"

    model = BedrockModel(model_id=model_id, region_name=region, temperature=0.4)

    agent_kwargs: dict[str, object] = {
        "model": model,
        "tools": [match_shifts],
        "system_prompt": SYSTEM_PROMPT,
    }
    # Sentinel lets callers explicitly pass callback_handler=None without us
    # overriding it with the Strands default.
    if callback_handler != "__default__":
        agent_kwargs["callback_handler"] = callback_handler

    return Agent(**agent_kwargs)
