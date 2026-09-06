# Demo Video Script (≤ 5 minutes)

**Total target: ~4:15** (leaves buffer under the 5:00 hard cap).
**Format:** screen recording of the live app + voiceover. No camera needed.
**Required beats (hackathon rules):** (1) the problem, (2) who it's for, (3) why it
matters — plus a clear working demo. **Say "Strands Agents SDK" out loud and show it.**

**Links on screen / in description:**
- Live app: https://volunteer-shift-matcher.streamlit.app/
- Project page: https://makendrang.github.io/volunteer-shift-matcher/
- Code: https://github.com/MakendranG/volunteer-shift-matcher

**Before you hit record:**
- Open the live app in a clean browser (hide bookmarks bar), zoom to ~110%.
- Have the GitHub repo open in a second tab (to show `matching.py` + `agent.py`).
- Do one warm-up run so it's responsive.
- Silence notifications.

---

## ⏱️ Timed shot list + voiceover

### 0:00–0:30 — Hook + the problem  *(screen: title slide, or the app hero)*
> "Every week, food banks and small nonprofits leave volunteer shifts unfilled —
> and it's usually not because volunteers don't exist. It's because one
> coordinator, already stretched thin, has to manually match everyone's
> availability and skills to every open shift, using spreadsheets and group texts.
> It's slow, it's error-prone, and shifts slip through the cracks. When a shift
> goes unfilled, food doesn't get sorted and neighbors don't get served."

### 0:30–0:50 — Who it's for + why it matters  *(screen: app hero / "what problem" expander)*
> "This is for volunteer coordinators at food banks and small nonprofits — the
> people holding a community together in their spare time. If we can do their
> matching and outreach in seconds, they get their evening back and more neighbors
> get helped. That's what this agent does."

### 0:50–1:15 — What it is + Strands callout  *(screen: the live app, top of page)*
> "Meet the Volunteer Shift Matcher — a Good Neighbor agent built with the
> **Strands Agents SDK**. You give it your open shifts and your volunteers, and it
> produces a match plan, drafts a warm confirmation for every assigned volunteer,
> and writes a 'help needed' broadcast for any shift it can't fully fill. Here's
> the live app — anyone can use it, no sign-up."

### 1:15–2:20 — The working demo  *(screen: edit inputs → click Match shifts → results)*
> "On the left are six open shifts across a weekend; on the right, eight
> volunteers with their skills and availability. I'll click **Match shifts**."
>
> *(click; results appear)*
>
> "Instantly: five shifts fully filled, and — this is the important part — one
> flagged as only **partially filled**. The Saturday driver shift needs two people
> but only one driver is available. A real coordinator lives in this imperfect
> world, and the agent doesn't hide it — it surfaces the gap."
>
> *(scroll to confirmations)*
>
> "For every assigned volunteer, it's drafted a warm, ready-to-send confirmation
> with their role, date, and time."
>
> *(scroll to the broadcast)*
>
> "And for that gap, it wrote a group-text-ready broadcast: 'we still need one more
> driver for Saturday, 10 to 1.' Copy, paste, send."

### 2:20–2:45 — Structured output  *(screen: expand the JSON + download button)*
> "It's not just pretty — everything's also structured JSON you can pipe into a
> scheduling system, plus a one-click download. Human-readable and
> machine-readable from the same run."

### 2:45–3:45 — How it works / the Strands architecture  *(screen: switch to repo — matching.py then agent.py; optionally the architecture diagram)*
> "Here's what makes it a real agent, not a single prompt. The matching itself is
> a deterministic Strands tool — `match_shifts` — just a Python function with the
> `@tool` decorator. It handles role eligibility, time coverage, and no
> double-booking, so the assignments are auditable and reproducible, never an LLM
> guess."
>
> *(switch to agent.py)*
>
> "And here's the agent: built with the Strands Agents SDK, given that tool and a
> system prompt, using Amazon Bedrock and Claude as the model. The Strands agent
> loop reasons, calls the tool for the facts, then uses the LLM only for the human
> part — writing the messages. Deterministic tool for correctness; LLM for the warm
> voice."

### 3:45–4:15 — Close  *(screen: back to the live app, or a closing slide with links)*
> "So: a job that eats a coordinator's evening, done in seconds — with an
> auditable plan, warm outreach, and honesty about the shifts it can't fill.
> It's open-source under MIT, it uses only synthetic data, and you can try the
> live app right now at volunteer-shift-matcher.streamlit.app. Built with the
> Strands Agents SDK, for the Agents for Humans hackathon. Thanks for watching."

---

## Optional: show the LIVE Bedrock agent (adds ~20s)

The public app runs keyless (offline-safe). If you want to show the *real*
LLM-drafted messages on camera, before recording open the sidebar
**"🔐 Test the LIVE agent with your own AWS"** panel and paste your own temporary
STS credentials, then run — the badge flips to "🟢 Live Strands agent · Amazon
Bedrock" and the messages are model-written. Mention: "these messages are drafted
live by Claude on Amazon Bedrock." Keep total under 5:00.

## Trimming tips (if you run long)
- Cut the JSON section (2:20–2:45) first; it's the most expendable.
- Keep the partial-shift moment and the Strands code — those score the most.

## Recording tools
- **OBS Studio** (free, all platforms): Screen Capture + Audio Input sources.
- macOS: QuickTime screen recording. Windows: Xbox Game Bar (Win+G).
- Export 1080p / 30fps, upload to YouTube (Public or Unlisted — not Private).
