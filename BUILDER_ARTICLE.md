<!--
=============================================================================
 builder.aws.com article — copy each field below into the matching editor box.
 The Body (after the "===== BODY =====" line) is the Markdown to paste into the
 article body. Title must contain "Agents for Humans" (hackathon bonus rule).
=============================================================================
-->

# ===== TITLE ===== (max 255 chars — paste into "Title")

Agents for Humans: Building a Volunteer Shift Matcher with the Strands Agents SDK


# ===== DESCRIPTION ===== (max 512 chars — paste into "Description")

How I built an AI agent that fills a food bank's empty volunteer shifts in seconds — using a deterministic Strands tool for auditable matching and Amazon Bedrock to draft the warm, human outreach.


# ===== TAGS ===== (max 5 — paste into "Tags")

strands-agents, amazon-bedrock, generative-ai, python, streamlit


# ===== CANONICAL URL ===== (optional — leave blank unless published elsewhere first)

(leave blank)


# ===== COVER IMAGE ===== (optional, 1200x675)

Suggestion: a screenshot of the live app's match-plan view
(https://volunteer-shift-matcher.streamlit.app/) with the amber "Partial" S3
driver card visible. Avoid text-heavy images.


<!-- ========================================================================= -->
# ===== BODY ===== (paste everything below this line into the article "Body")
<!-- ========================================================================= -->

*How I built an AI agent that fills a food bank's empty volunteer shifts in
seconds — using a deterministic tool for the facts and Amazon Bedrock for the
human touch.*

> **Try it live:** https://volunteer-shift-matcher.streamlit.app/
> **Code (MIT):** https://github.com/MakendranG/volunteer-shift-matcher
> **Track:** Good Neighbor Agents · *Agents for Humans* hackathon

---

## The problem that started it

I didn't start with an AI idea. I started with a person.

Picture the volunteer coordinator at a small food bank. She has a spreadsheet of
who's free and when, a list of shifts that need covering this weekend, and a
group chat that never stops buzzing. Every week she plays the same exhausting
game: cross-referencing availability against skills against shift times, in her
head, while doing five other jobs. Shifts fall through the cracks — and when a
shift goes unfilled, food doesn't get sorted and neighbors don't get served.

That's the exact pain the *Good Neighbor Agents* track calls out: **"matching
volunteers to the shifts a food bank actually needs."** So I wrote my
one-sentence problem statement and refused to move until it was concrete:

> Food banks and small nonprofits chronically have unfilled volunteer shifts —
> not because volunteers don't exist, but because manually matching availability
> and skills to open shifts is slow and error-prone for a coordinator who is
> already stretched thin.

Everything I built traces back to that sentence.

## The key design decision: deterministic tool + LLM drafting

The temptation with agents is to throw everything at the model: "here are the
shifts and volunteers, figure it out." But volunteer scheduling is a place where
a wrong answer has real consequences — you don't want an LLM *hallucinating* that
someone is available when they're not.

So I split the work in two:

1. **A deterministic Python tool does the matching.** Who is assigned to which
   shift is computed in plain, auditable Python — role eligibility, full
   time-window coverage, no double-booking, and honest flagging of any shift that
   can't be filled. A coordinator (or a judge) can read exactly *why* each
   decision was made.
2. **The LLM does what LLMs are great at — the human touch.** It takes that
   verified plan and drafts warm, ready-to-send confirmation messages for each
   volunteer, plus "help needed" broadcasts for the gaps.

This is what makes it a genuine agent rather than a single prompt: the model
reasons, calls a tool, and composes language around the tool's output.

## Building it with the Strands Agents SDK

The Strands Agents SDK made this split almost trivial to express. A custom tool
is just a decorated Python function:

```python
from strands import tool

@tool
def match_shifts(shifts: list[dict], volunteers: list[dict]) -> dict:
    """Deterministically match volunteers to open shifts and flag any gaps."""
    return compute_match_plan(shifts, volunteers)
```

And the agent is a few lines that wire the tool and a system prompt to a model:

```python
from strands import Agent
from strands.models import BedrockModel

agent = Agent(
    model=BedrockModel(model_id="global.anthropic.claude-sonnet-4-6",
                       region_name="us-west-2", temperature=0.4),
    tools=[match_shifts],
    system_prompt=SYSTEM_PROMPT,   # "always call match_shifts, then draft messages…"
)
```

The system prompt instructs the agent to *always* call `match_shifts` for the
assignments (never guess), then use the result to draft the messages and return a
single structured JSON object. Strands runs the agent loop — reason → call tool →
compose response — and I get back both the structured plan and the natural
language, every time.

## Using AWS

The model provider is **Amazon Bedrock** (Claude Sonnet 4), which is the Strands
default. A detail I'm proud of: **there are no hardcoded credentials anywhere.**
The agent reads everything from the environment (or an IAM role), and `.env` is
gitignored so no key can ever be committed.

That credential discipline paid off when I added a visual UI and a public demo.

## Making it real: a visual UI and a public demo

A CLI proves the agent works, but judges (and coordinators) want to *see* it. So
I built a **Streamlit** front-end over the exact same agent: paste your shifts and
volunteers, click one button, and get a colour-coded match plan (filled / partial
/ unfilled), the drafted confirmations, and the help-needed broadcasts.

Then I deployed it free on **Streamlit Community Cloud** so anyone can try it:
https://volunteer-shift-matcher.streamlit.app/

Here's the security decision I'm most happy with. A public app with my AWS keys
would let the whole internet spend my Bedrock budget. So the public demo runs
**keyless** — it auto-detects the absence of credentials and defaults to an
offline deterministic mode that still shows the full matching. For anyone who
wants the *real* Bedrock experience, there's an optional panel to paste their
**own temporary STS credentials** — held only in their browser session, never
stored, and billed to their own account. (A web app can't borrow your AWS Console
login — browser cross-site isolation forbids it — so short-lived STS credentials
are the correct, secure equivalent.)

## The insight that made the demo honest

Early on, my sample data made every shift fill perfectly. It looked great — and
it was misleading. Real coordinators don't live in a perfect world.

So I deliberately engineered the sample data so that one shift — a Saturday driver
slot needing two people — can only be half-filled with the available pool. Now the
demo shows the feature that actually matters: the agent flags the gap
("**need 1 more person for Saturday driver, 10am–1pm**") and drafts the broadcast
to close it. Handling the imperfect case *is* the product.

## What I'd do next

- Two-way integration: send the confirmations over SMS/Slack and ingest replies.
- Recurring shifts and volunteer reliability history.
- A "regenerate message in a warmer/shorter tone" button powered by the same agent.
- Optionally deploy to Amazon Bedrock AgentCore Runtime for a managed HTTP endpoint.

## Takeaways for other builders

1. **Start with a person, not a prompt.** The one-sentence problem statement kept
   every decision honest.
2. **Let deterministic code own the decisions that must be correct; let the LLM
   own the language.** That division is what makes an agent trustworthy.
3. **Design your demo around the imperfect case** — that's where the value shows.
4. **Never ship keys.** Environment variables, gitignored `.env`, and a keyless
   public demo meant I could open-source everything with zero anxiety.

Strands made the agent itself the easy part — a decorated function and a few
lines to wire it up — which freed me to spend my time on the things that actually
make a Good Neighbor Agent good: correctness, honesty about gaps, and a warm voice.

**Try it:** https://volunteer-shift-matcher.streamlit.app/ ·
**Code:** https://github.com/MakendranG/volunteer-shift-matcher

*Built for the Agents for Humans hackathon — Good Neighbor Agents track. Uses only
synthetic sample data; no real personal information.*
