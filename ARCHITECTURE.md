# Architecture

## Problem being solved

Food banks and small nonprofits chronically have unfilled volunteer shifts — not
because volunteers don't exist, but because manually matching volunteer
availability/skills to open shifts (via spreadsheets or group texts) is slow and
error-prone for a coordinator who is already stretched thin. This system
automates that matching and drafts the outreach messages.

## Data flow

> A rendered image of this diagram is available at
> [`docs/architecture.png`](./docs/architecture.png) (also used for the Devpost
> submission). The Mermaid source below covers the five elements the hackathon
> FAQ asks for: user interface, the Strands agent + agentic loop, tools &
> integrations, AWS services used, and output.

```mermaid
flowchart LR
    UI["User interface<br/>(Streamlit web app / CLI)"]

    subgraph Inputs
        V["Volunteer data<br/>(name, email, roles,<br/>availability windows)"]
        S["Shift data<br/>(role, date, time,<br/>min_volunteers_needed)"]
    end

    UI --> AG
    V --> AG
    S --> AG

    subgraph Agent["shift_matcher_agent (Strands Agents SDK)"]
        direction TB
        AG["Agent loop (LLM orchestration)<br/>model → tools → reasoning → response"] -->|calls tool| T["Tool: match_shifts @tool<br/>(deterministic Python:<br/>eligibility + greedy assign,<br/>flags gaps)"]
        T -->|match plan JSON| DRAFT["LLM drafting layer<br/>AWS: Amazon Bedrock (Claude)<br/>warm confirmations + broadcasts"]
    end

    AG --> OUT
    DRAFT --> OUT

    subgraph Output
        OUT["Structured JSON<br/>+ human-readable / visual summary"]
        OUT --> C["Confirmation messages<br/>(per assigned volunteer)"]
        OUT --> B["Help-needed broadcasts<br/>(per unfilled/partial shift)"]
    end
```

**Elements (per hackathon FAQ):** *User interface* — Streamlit web app or CLI ·
*Strands Agents* — the `shift_matcher_agent` and its agentic loop · *Tools &
integrations* — the deterministic `match_shifts` `@tool` · *AWS services* — Amazon
Bedrock (Claude Sonnet 4) for message drafting · *Output* — structured JSON plus a
visual/console summary (confirmations + help-needed broadcasts).

## How data flows through the system (in words)

Volunteer data and shift data enter the `shift_matcher_agent`, a Strands agent
built on the Strands Agents SDK. The agent's LLM loop first calls the
deterministic `match_shifts` custom tool, which performs the actual eligibility
checking and greedy assignment in pure Python — making the "who is assigned to
what" decision auditable and reproducible rather than an LLM guess. The agent
then feeds that structured match plan into its LLM drafting layer, which writes
warm per-volunteer confirmation messages and, for any shift the tool flagged as
partially filled or unfilled, a friendly "help needed" broadcast describing the
specific gap. Finally, the CLI prints both a structured JSON object and a clean
human-readable summary to the console.
