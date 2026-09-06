# Devpost Submission Pack

Everything you need to paste into the Devpost submission form, plus a
pre-submit checklist mapped to the official rules. Fill in the `<...>`
placeholders before submitting.

---

## 1. Project name

**Volunteer Shift Matcher**

## 2. Track

**Good Neighbor Agents** — the rules name this exact use case: *"matching
volunteers to the shifts a food bank actually needs."*

## 3. Elevator pitch (one line, for the Devpost tagline field)

> A Strands agent that fills a food bank's volunteer shifts in seconds —
> auditable matching plus warm, ready-to-send outreach, and it's honest about
> the gaps it can't fill.

---

## 4. Text description (paste into the "About the project" field)

*Judges may score on this text + your video alone, so it leads with the problem
and names Strands explicitly.*

### The problem

Food banks and small nonprofits chronically have unfilled volunteer shifts — not
because volunteers don't exist, but because manually matching volunteer
availability and skills to open shifts (via spreadsheets and group texts) is slow
and error-prone for a coordinator who is already stretched thin. A shift that
goes unfilled means food doesn't get sorted and neighbors don't get served.

### Who it's for

Volunteer coordinators at food banks, pantries, and small nonprofits — the people
who juggle scheduling on top of everything else and just need the matching and
outreach done for them.

### What it does

Given a list of open shifts (role, date, time, how many people are needed) and a
pool of volunteers (skills and availability), **Volunteer Shift Matcher**:

1. Produces an **auditable match plan** — who is assigned to each shift.
2. Drafts a **warm confirmation message** for every assigned volunteer.
3. For any shift it can't fully fill, drafts a ready-to-send **"help needed"
   broadcast** describing the exact gap (e.g. *"need 1 more driver for Saturday,
   10am–1pm"*).
4. Outputs both structured JSON (for automation) and a clean console summary.

Crucially, it's **honest about the shifts it can't fill** — instead of hiding a
gap, it surfaces it and writes the outreach to close it.

### How it works

It's built with the **Strands Agents SDK**. The agent calls a deterministic
custom tool, `match_shifts`, written in plain Python — so the "who goes where"
decision is reproducible and auditable, not an LLM guess. The agent's language
model (Amazon Bedrock, Claude Sonnet 4) then turns that plan into the warm,
natural-language confirmation and broadcast messages. This split — deterministic
tool for the facts, LLM for the human touch — is what makes it a genuine,
non-trivial agent rather than a single prompt. See the architecture diagram in
the repo for the full data flow.

### Built with

- **Strands Agents SDK** (the agent, the `@tool`-decorated `match_shifts`
  function, and the LLM drafting layer)
- **Amazon Bedrock** — Claude Sonnet 4
- **Python 3.10+**

---

## 5. "Built With" tags (Devpost tags field)

`strands-agents-sdk`, `amazon-bedrock`, `python`, `aws`, `ai-agents`

---

## 6. Links to fill in

- **Public repo URL:** `https://github.com/MakendranG/volunteer-shift-matcher`
- **Demo video (≤5 min):** `<YouTube/Vimeo unlisted or public link>`
- **AWS Builder ID:** `<your Builder ID>`
- **(Optional) live demo link:** `<if you deploy one — scores higher>`
- **(Bonus) builder.aws.com post:** `<link, title must contain "Agents for Humans">`

---

## 7. Pre-submit checklist (mapped to official rules)

Required:
- [x] **Text description** completed (section 4 above) — leads with the problem,
      names Strands, explains what/who/how.
- [x] **Public code repo URL** — repo is public:
      https://github.com/MakendranG/volunteer-shift-matcher (verified PUBLIC).
- [x] **All source code + setup instructions** to run cold — README covers this.
- [x] **MIT or Apache license visible in the repo About section** — MIT `LICENSE`
      pushed; GitHub auto-detected it (About shows "MIT License", verified via API).
- [x] **README** present. (in repo)
- [x] **Architecture diagram** present. (`ARCHITECTURE.md`, Mermaid)
- [ ] **Demo video (≤5 min)** recorded and uploaded — covers problem / who /
      why + shows it working end-to-end. Script in `DEMO_SCRIPT.md`.  ← TODO (you)
- [ ] **AWS Builder ID** entered on the submission form.  ← TODO (you)

Scoring boosters (optional):
- [ ] Live demo link (raises Technical Implementation score).
- [ ] AgentCore deployment (see `DEPLOY_AGENTCORE.md`) — raises Technical score.
- [ ] builder.aws.com post with "Agents for Humans" in the title (bonus points).

Safety before you push public:
- [x] `.env` is gitignored and NOT committed (only `.env.example` is) — verified,
      no `.env`/`.venv` on the remote.
- [x] No hardcoded API keys anywhere — secret scan clean.
- [x] Virtual env (`.venv/`) is gitignored and not committed.

AI-tool disclosure (per rules):
- [x] This project's code was written new during the submission period with the
      help of an AI coding assistant, which the rules explicitly allow. No
      pre-existing/reused AI-built project is incorporated. Disclose if your org
      requires it.
