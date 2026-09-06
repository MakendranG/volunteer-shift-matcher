<!--
Devpost submission content — copy each section into the matching field on Devpost.
Items marked "⚠️ YOU PROVIDE" require your input (video, Builder ID, blog URL).
-->

# Devpost Submission — Volunteer Shift Matcher

## Project name (60 char limit)

```
Volunteer Shift Matcher
```

## Elevator pitch (200 char limit)

```
An AI agent that fills a food bank's volunteer shifts in seconds — auditable matching plus warm, ready-to-send outreach, and it's honest about the gaps it can't fill. Built with Strands Agents SDK.
```

## About the project (Project Story — paste as Markdown)

```markdown
## Inspiration

I didn't start with an AI idea — I started with a person. Picture the volunteer coordinator at a small food bank: a spreadsheet of who's free when, a list of shifts that need covering this weekend, and a group chat that never stops buzzing. Every week she cross-references availability against skills against shift times, in her head, while doing five other jobs. Shifts fall through the cracks — and an unfilled shift means food doesn't get sorted and neighbors don't get served. The Good Neighbor Agents track names this exact pain: "matching volunteers to the shifts a food bank actually needs."

## What it does

Given a list of open shifts (role, date, time, how many people are needed) and a pool of volunteers (skills + availability), the agent:

- Produces an **auditable match plan** — who is assigned to each shift.
- Drafts a **warm confirmation message** for every assigned volunteer.
- For any shift it can't fully fill, drafts a ready-to-send **"help needed" broadcast** describing the exact gap (e.g. "need 1 more driver for Saturday, 10am–1pm").
- Outputs both structured JSON and a clean, colour-coded visual summary.

Crucially, it's **honest about the shifts it can't fill** — instead of hiding a gap, it surfaces it and writes the outreach to close it.

## How we built it

It's built with the **Strands Agents SDK**. The design splits the work in two:

1. A deterministic Python **`@tool` (`match_shifts`)** computes the assignments — role eligibility, full time-window coverage, no double-booking, and gap flagging. Because it's plain Python, the "who goes where" decision is reproducible and auditable, not an LLM guess.
2. The agent's LLM (**Amazon Bedrock**, Claude Sonnet 4) turns that verified plan into the warm, natural-language confirmation and broadcast messages.

We wrapped the same agent in a **Streamlit** UI and deployed it free on Streamlit Community Cloud so anyone can try it. The public demo runs keyless (offline-safe default); an optional panel lets a visitor run the live Bedrock agent with their own temporary STS credentials — session-only, never stored.

## Challenges we ran into

- **Making the demo honest.** Our first sample data filled every shift perfectly — which was misleading. We deliberately engineered the data so one shift (a Saturday driver slot needing two people) stays partially filled, so the demo shows the feature that matters most: flagging and broadcasting real gaps.
- **Public demo security.** A public app with our AWS keys would let anyone spend our Bedrock budget. We solved it with a keyless default plus optional bring-your-own temporary credentials, so no keys are ever exposed.
- **Keeping matching trustworthy.** We kept assignment logic in deterministic Python (with a full pytest suite) rather than trusting the LLM to schedule.

## What we learned

Let deterministic code own the decisions that must be correct, and let the LLM own the language. That division is what makes an agent trustworthy — and Strands made wiring a custom tool to a model almost trivial, freeing us to focus on correctness, honesty about gaps, and a warm voice.

## What's next for Volunteer Shift Matcher

Two-way SMS/Slack integration to send confirmations and ingest replies, recurring shifts, volunteer reliability history, and an optional Amazon Bedrock AgentCore deployment for a managed endpoint.

## Note on data

This project uses only synthetic sample data — no real personal information — and no API keys are committed anywhere.
```

## Built with (tags — up to 25)

```
strands-agents-sdk, amazon-bedrock, aws, python, streamlit, claude, generative-ai, ai-agents
```

## "Try it out" links

- Live demo: https://volunteer-shift-matcher.streamlit.app/
- Project page: https://makendrang.github.io/volunteer-shift-matcher/
- Code repo: https://github.com/MakendranG/volunteer-shift-matcher

## Video demo link

⚠️ YOU PROVIDE — YouTube/Vimeo URL (record using `DEMO_SCRIPT.md`).

## PUBLIC URL to your code repo

```
https://github.com/MakendranG/volunteer-shift-matcher
```

## Architecture diagram (REQUIRED — upload a file)

Upload `docs/architecture.png` (2400×1350 PNG, 3:2 ratio) from this repo.
Source: `docs/architecture.svg` / `docs/architecture.mmd` (regenerate with
`python docs/make_diagram.py`).

## AWS Builder ID

⚠️ YOU PROVIDE.

## URL to your live demo link

```
https://volunteer-shift-matcher.streamlit.app/
```

## Testing instructions (if applicable)

Open the live demo, keep the sample data (or edit it), and click **Match shifts** —
it runs keyless in Offline mode. To test the live Strands + Bedrock agent, open the
sidebar "🔐 Test the LIVE agent with your own AWS" panel and paste your own temporary
STS credentials. Or run locally: `pip install -r requirements.txt` then
`python run_agent.py` (or `streamlit run streamlit_app.py`).

## URL to your Optional Bonus Blog Post (builder.aws.com)

⚠️ YOU PROVIDE — publish `BUILDER_ARTICLE.md` on builder.aws.com (title must contain
"Agents for Humans"), then paste the public URL here.
