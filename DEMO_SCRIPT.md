# Demo Video Script & Storyboard

**Target length:** ≤ 5:00 (aim for 3:30–4:00 — shorter is stronger).
**Format allowed:** slides + screen recording + voiceover. No on-camera face needed.
**Required pitch beats (per hackathon rules):** (1) the problem, (2) who it's for,
(3) why it matters — plus a clear demo of the project *working end-to-end*.
**Make Strands impossible to miss:** say "Strands Agents SDK" out loud and show it
on screen (the `@tool` + `Agent` code, and the tool being called in the run).

Recording tips:
- Do a dry run of `python run_agent.py` before recording so the model output is warm.
- Increase terminal font size (18–22pt) so code and output are readable.
- If your live Bedrock run is slow or flaky on the day, record `--offline` as backup;
  it produces the same match plan and template messages with no network dependency.

---

## Storyboard (6 scenes)

| # | Time | On screen | Voiceover |
|---|------|-----------|-----------|
| 1 | 0:00–0:35 | Title slide: "Volunteer Shift Matcher — a Good Neighbor Agent, built with the Strands Agents SDK." Then a photo/illustration of a food-bank coordinator buried in a spreadsheet + group texts. | *(Problem)* "Food banks and small nonprofits constantly have volunteer shifts that go unfilled — not because volunteers don't exist, but because one stretched-thin coordinator has to manually cross-reference everyone's availability and skills against every open shift, using spreadsheets and group texts. It's slow, and shifts fall through the cracks." |
| 2 | 0:35–1:00 | Slide: "Who it's for" — icon of a volunteer coordinator; "Food banks • pantries • small nonprofits." | *(Who + why)* "This is for volunteer coordinators — the people holding a community together in their spare time. When a shift goes unfilled, meals don't get sorted and neighbors don't get served. Saving them time directly translates into more people helped." |
| 3 | 1:00–1:40 | Screen recording: open `ARCHITECTURE.md`, show the Mermaid diagram. Briefly point at the flow: Volunteer + Shift data → Strands Agent → `match_shifts` tool → LLM drafting → output. | *(How it works)* "It's a Strands agent. Here's the flow: volunteer and shift data go into the agent. The agent calls a deterministic tool called `match_shifts` — plain Python, so the assignments are auditable, not an LLM guess. Then the agent's language model turns that plan into warm, ready-to-send messages." |
| 4 | 1:40–2:20 | Screen recording: open `shift_matcher/matching.py`, scroll to the `@tool def match_shifts`. Then open `shift_matcher/agent.py`, show `Agent(model=..., tools=[match_shifts], system_prompt=...)`. | *(Strands, front and center)* "Here's the actual Strands code. `match_shifts` is a custom tool — just a Python function with the `@tool` decorator. And here's the agent itself: built with the Strands Agents SDK, given the tool and a system prompt. This is a genuine agent that reasons and calls tools — not a single prompt." |
| 5 | 2:20–3:50 | Screen recording: run `python run_agent.py`. Let the MATCH PLAN print. Highlight **S3 driver — PARTIAL (1/2)** and the GAP line. Scroll through a couple of CONFIRMATION MESSAGES, then the HELP-NEEDED BROADCAST for S3. | *(Working demo)* "Let's run it. The agent ingests six shifts and eight volunteers, calls the tool, and produces a match plan. Five shifts are fully filled. And notice this one — Saturday's driver shift — the agent flags it as only partially filled: it found one driver but needs two. That's the realistic case coordinators live in. For every assigned volunteer it drafts a warm confirmation… and for that gap, it writes a 'help needed' broadcast you can paste straight into a group text: 'we still need one more driver for Saturday, 10 to 1.'" |
| 6 | 3:50–4:20 | Slide: recap 3 bullets — "Auditable matching (Python tool) • Warm outreach (LLM) • Flags the gaps, doesn't hide them." Then: "Built with the Strands Agents SDK. MIT licensed. Repo: github.com/MakendranG/volunteer-shift-matcher." | *(Close)* "So: deterministic, auditable matching from a Strands tool; warm, human outreach from the model; and it's honest about the shifts it can't fill. It takes a job that eats a coordinator's evening and does it in seconds. Built with the Strands Agents SDK. Thanks for watching." |

---

## Tight voiceover script (continuous read, ~40s under budget)

> Food banks and small nonprofits constantly have volunteer shifts that go unfilled — not because volunteers don't exist, but because one stretched-thin coordinator has to manually match everyone's availability and skills to every open shift, with spreadsheets and group texts. It's slow, and shifts fall through the cracks.
>
> This is for those coordinators. When a shift goes unfilled, meals don't get sorted and neighbors don't get served — so saving them time directly helps more people.
>
> It's a Strands agent. Volunteer and shift data go in. The agent calls a deterministic tool, `match_shifts` — plain Python, so the assignments are auditable, not a guess — and then the model turns that plan into ready-to-send messages.
>
> Here's the Strands code: `match_shifts` is a custom tool, just a Python function with the `@tool` decorator, and here's the agent, built with the Strands Agents SDK, wired to that tool.
>
> Let's run it. Six shifts, eight volunteers. Five shifts fill completely. This one — Saturday's driver shift — the agent flags as partially filled: one driver found, two needed. For every match it drafts a warm confirmation, and for the gap it writes a 'help needed' broadcast ready for a group text.
>
> Deterministic matching, warm outreach, honest about the gaps — a coordinator's evening of work, done in seconds. Built with the Strands Agents SDK. Thanks for watching.

---

## Exact commands to show on screen

```bash
# 1. show it's real code
sed -n '/@tool/,/return compute_match_plan/p' shift_matcher/matching.py   # the tool
sed -n '/def build_agent/,/return Agent/p' shift_matcher/agent.py         # the agent

# 2. run the live agent (Strands + Bedrock)
python run_agent.py

# 3. backup if network is flaky on the day (no LLM/creds needed):
python run_agent.py --offline
```
