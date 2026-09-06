# Volunteer Shift Matcher

An AI agent that helps volunteer coordinators at food banks and small nonprofits
fill open volunteer shifts in seconds. Given a list of open shifts and a pool of
volunteers, it produces an auditable match plan, drafts a warm confirmation
message for every assigned volunteer, and writes a ready-to-send "help needed"
broadcast for any shift it can't fully fill. Built with the
[Strands Agents SDK](https://strandsagents.com/).

> Submission for the **Agents for Humans** hackathon — *Good Neighbor Agents* track.
>
> **Repository:** https://github.com/MakendranG/volunteer-shift-matcher

## The problem

Food banks and small nonprofits chronically have unfilled volunteer shifts — not
because volunteers don't exist, but because manually matching volunteer
availability/skills to open shifts (via spreadsheets or group texts) is slow and
error-prone for a coordinator who is already stretched thin.

In plain language: a real person is sitting with a spreadsheet of who's free
when, a list of shifts that need covering, and a group chat — trying to mentally
cross-reference all of it while doing five other jobs. Shifts fall through the
cracks. This agent does that cross-referencing instantly and even writes the
outreach messages.

## Who it's for

Volunteer coordinators at food banks and small nonprofits — the people who
juggle volunteer scheduling on top of everything else and just need the matching
and outreach done for them.

## How it works

1. **You provide** two lists: open **shifts** (role, date, time, how many people
   are needed) and **volunteers** (name, email, roles they'll do, when they're
   free).
2. **The Strands agent** calls a deterministic `match_shifts` tool that computes
   exactly who should be assigned to each shift and flags any gaps. Because the
   matching is plain Python, the "who goes where" decision is fully auditable —
   not an LLM guess.
3. **The LLM drafting layer** turns that plan into warm, ready-to-send messages:
   a confirmation for each assigned volunteer, and a "help needed" broadcast for
   each shift that's still short.
4. **You get** both structured JSON (for automation) and a clean console summary.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for a Mermaid diagram of the full data
flow.

## Built With

- **[Strands Agents SDK](https://strandsagents.com/)** — the agent, the
  `@tool`-decorated `match_shifts` function, and the LLM drafting layer.
- **Amazon Bedrock** (Claude Sonnet 4) — the default model provider for drafting
  natural-language messages.
- **Python 3.10+**.

## Setup

A stranger should be able to clone this and run it cold. Here's everything:

### Prerequisites

- **Python 3.10 or newer** (`python3 --version` to check).
- For the full LLM experience: **AWS credentials with Amazon Bedrock access** to
  Claude Sonnet 4. (No credentials? Use `--offline` mode below — it still runs
  the full match plan and produces template messages.)

### 1. Clone and enter the project

```bash
git clone https://github.com/MakendranG/volunteer-shift-matcher.git
cd volunteer-shift-matcher
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your own values. **No secrets are committed to
this repo**, and `.env` is gitignored.

```bash
cp .env.example .env
# then edit .env with your AWS credentials + region
```

Alternatively, configure AWS the standard way with `aws configure`, or rely on
an IAM role. The agent reads all credentials from the environment — there are no
hardcoded keys anywhere in the code.

### 4. Run the demo

```bash
# Full agent (Strands + Amazon Bedrock):
python run_agent.py

# No AWS credentials? Run the deterministic matcher offline (still a full demo):
python run_agent.py --offline

# Use your own data:
python run_agent.py --shifts my_shifts.json --volunteers my_volunteers.json
```

### 4b. Or launch the visual web UI (recommended for the demo)

A [Streamlit](https://streamlit.io/) front-end over the same Strands agent — edit
shifts/volunteers, click a button, and see a colour-coded match plan and the
drafted messages:

```bash
streamlit run streamlit_app.py
```

Then open the URL it prints (default http://localhost:8501). Use the sidebar to
switch between **Live agent (Strands + Bedrock)** and **Offline** mode. If live
mode has no credentials, the app automatically falls back to offline.

The sidebar also has an optional **"🔐 Test the LIVE agent with your own AWS"**
panel: a visitor can paste their own **temporary/STS** credentials to run the real
Strands + Bedrock agent on their own account. Credentials are session-only and
never stored — their usage bills to their account, not the host's.

**Live public demo:** deployable free on
[Streamlit Community Cloud](https://streamlit.io/cloud) — point it at this repo
with `streamlit_app.py` as the entrypoint (see `DEPLOY_STREAMLIT.md`).

### 5. Run the tests

```bash
python -m pytest
```

## Sample output

Real output from `python run_agent.py` against the included sample data. Notice
shift **S3** can only get 1 of the 2 drivers it needs — the agent handles this
realistic imperfect scenario by flagging the gap and drafting a broadcast:

```
======================================================================
MATCH PLAN
======================================================================
6 shifts | 5 filled | 1 partially filled | 0 unfilled

[FILLED] S1: food sorting on 2026-09-12 9:00am-12:00pm (3/3)
         - James Chen <james.chen@example.com>
         - Maria Alvarez <maria.alvarez@example.com>
         - Priya Patel <priya.patel@example.com>
[PARTIAL] S3: driver on 2026-09-12 10:00am-1:00pm (1/2)
         - Sofia Rossi <sofia.rossi@example.com>
         ! GAP: need 1 more person for 2026-09-12 driver, 10:00-13:00
[FILLED] S2: front desk on 2026-09-12 1:00pm-4:00pm (2/2)
         - David Okoro <david.okoro@example.com>
         - Priya Patel <priya.patel@example.com>
...

======================================================================
CONFIRMATION MESSAGES (10)
======================================================================
To James Chen <james.chen@example.com> [S1]:
  Hi James! 👋 Just confirming your volunteer shift with us — you're all set for
  food sorting on Saturday, September 12th from 9:00 AM to 12:00 PM. We're so
  grateful for your help! See you then. 😊
...

======================================================================
HELP-NEEDED BROADCASTS (1)
======================================================================
[S3] 🚨 Volunteer needed! We still need 1 more driver for this Saturday,
     September 12th from 10:00 AM to 1:00 PM. If you're available and can drive,
     please sign up or reply to this message — every hand makes a huge
     difference. Thank you! 🙏
```

The full run also prints a `STRUCTURED JSON OUTPUT` block containing the
`match_plan`, `confirmation_messages`, and `help_needed_broadcasts` for easy
integration with other tools.

## Project structure

```
volunteer-shift-matcher/
├── shift_matcher/
│   ├── __init__.py
│   ├── matching.py       # deterministic match_shifts @tool + pure-Python logic
│   └── agent.py          # the shift_matcher_agent Strands agent + system prompt
├── sample_data/
│   ├── shifts.json       # 6 shifts across 3 days
│   └── volunteers.json   # 8 volunteers (engineered so 1 shift stays partial)
├── tests/
│   └── test_matching.py  # pytest suite for the matching logic (no LLM needed)
├── run_agent.py          # CLI entrypoint
├── requirements.txt
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── LICENSE
└── README.md
```

## A note on data & privacy

This project uses **only synthetic sample data** in `sample_data/`. All names,
email addresses, and schedules are made up for the demo — there is **no real
personal information** anywhere in this repository, and no real API keys are
committed.

## License

MIT — see [`LICENSE`](./LICENSE). (Update the copyright holder placeholder to
your name.)
