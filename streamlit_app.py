"""Streamlit UI for the Volunteer Shift Matcher — a Good Neighbor Agent built
with the Strands Agents SDK.

Run locally:
    streamlit run streamlit_app.py

A visual front-end over the SAME Strands agent used by the CLI. A coordinator
pastes/edits their shifts and volunteers, clicks one button, and instantly sees a
colour-coded match plan, warm confirmation messages, and "help needed" broadcasts
for any shift that can't be filled.

Problem being solved: food banks and small nonprofits chronically have unfilled
volunteer shifts because manually matching availability/skills to open shifts is
slow and error-prone for an already-stretched coordinator.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

# Load .env if present (keeps AWS creds out of the code). Safe if not installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001
    pass

from shift_matcher.pipeline import fmt_time, run_offline, run_with_agent

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "sample_data"

st.set_page_config(
    page_title="Volunteer Shift Matcher",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------- #
# Global styling — custom CSS for a polished, modern look
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      /* ---- palette ---- */
      :root {
        --brand:#0f766e; --brand2:#14b8a6;
        --ok:#16a34a; --okbg:#ecfdf5; --okbd:#a7f3d0;
        --warn:#b45309; --warnbg:#fffbeb; --warnbd:#fde68a;
        --bad:#dc2626; --badbg:#fef2f2; --badbd:#fecaca;
        --ink:#0f172a; --muted:#64748b; --line:#e2e8f0;
      }
      /* widen content a touch and add breathing room */
      .block-container {padding-top: 1.2rem; max-width: 1250px;}

      /* ---- hero header ---- */
      .hero {
        background: linear-gradient(120deg,#0f766e 0%,#14b8a6 55%,#22d3ee 100%);
        color:#fff; border-radius:20px; padding:30px 34px; margin-bottom:8px;
        box-shadow:0 12px 30px rgba(15,118,110,.28);
      }
      .hero h1 {color:#fff; font-size:2.15rem; font-weight:800; margin:0 0 6px 0; letter-spacing:-.5px;}
      .hero p  {color:#e6fffb; font-size:1.05rem; margin:0; max-width:820px; line-height:1.5;}
      .hero .pill {
        display:inline-block; background:rgba(255,255,255,.18); color:#fff;
        padding:4px 12px; border-radius:999px; font-size:.78rem; font-weight:600;
        margin-bottom:12px; border:1px solid rgba(255,255,255,.35); backdrop-filter:blur(4px);
      }

      /* ---- metric tiles ---- */
      .tile {
        background:#fff; border:1px solid var(--line); border-radius:16px;
        padding:16px 18px; text-align:center; box-shadow:0 2px 8px rgba(2,6,23,.05);
      }
      .tile .num {font-size:2rem; font-weight:800; line-height:1; color:var(--ink);}
      .tile .lbl {font-size:.82rem; color:var(--muted); margin-top:6px; font-weight:600; text-transform:uppercase; letter-spacing:.4px;}

      /* ---- shift cards ---- */
      .shift {
        border-radius:14px; padding:14px 18px; margin-bottom:12px;
        border:1px solid var(--line); box-shadow:0 2px 10px rgba(2,6,23,.05);
      }
      .shift .top {display:flex; justify-content:space-between; align-items:center; gap:10px;}
      .shift .title {font-size:1.08rem; font-weight:700; color:var(--ink);}
      .shift .when {font-weight:500; color:var(--muted); font-size:.92rem;}
      .shift .count {font-weight:800; font-size:1.05rem; padding:3px 12px; border-radius:999px;}
      .shift .who {margin:10px 0 0 0; padding:0; list-style:none; display:flex; flex-wrap:wrap; gap:8px;}
      .shift .who li {
        background:#f1f5f9; border:1px solid var(--line); border-radius:999px;
        padding:4px 12px; font-size:.86rem; color:#334155;
      }
      .shift .gap {margin-top:10px; font-weight:700; font-size:.9rem;}
      .badge {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.74rem; font-weight:700; text-transform:uppercase; letter-spacing:.4px;}

      /* ---- message cards ---- */
      .msg {
        background:#fff; border:1px solid var(--line); border-left:4px solid var(--brand);
        border-radius:12px; padding:13px 16px; margin-bottom:10px; box-shadow:0 1px 6px rgba(2,6,23,.04);
      }
      .msg .to {font-weight:700; color:var(--ink); font-size:.92rem;}
      .msg .meta {color:var(--muted); font-size:.8rem; margin-bottom:6px;}
      .msg .body {color:#334155; font-size:.94rem; line-height:1.5;}
      .msg.broadcast {border-left-color:var(--warn); background:var(--warnbg);}

      .section-h {font-size:1.15rem; font-weight:800; color:var(--ink); margin:6px 0 10px 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def load_sample(name: str) -> str:
    return (SAMPLE / name).read_text(encoding="utf-8")


# status -> (emoji, text color, bg, border, label)
STATUS = {
    "filled": ("✅", "#16a34a", "#ecfdf5", "#a7f3d0", "Filled"),
    "partially_filled": ("⚠️", "#b45309", "#fffbeb", "#fde68a", "Partial"),
    "unfilled": ("❌", "#dc2626", "#fef2f2", "#fecaca", "Unfilled"),
}


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <span class="pill">🏆 Agents for Humans · Good Neighbor track · Built with the Strands Agents SDK</span>
          <h1>🤝 Volunteer Shift Matcher</h1>
          <p>Fill a food bank's volunteer shifts in seconds. Paste your open shifts
          and volunteers — the AI agent builds an auditable match plan, drafts warm
          confirmation messages, and writes <em>help-needed</em> broadcasts for any
          gap it can't fill.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(summary: dict) -> None:
    tiles = [
        ("📋", summary["total_shifts"], "Total shifts", "#0f172a"),
        ("✅", summary["filled"], "Filled", "#16a34a"),
        ("⚠️", summary["partially_filled"], "Partial", "#b45309"),
        ("❌", summary["unfilled"], "Unfilled", "#dc2626"),
    ]
    cols = st.columns(4)
    for col, (icon, num, lbl, color) in zip(cols, tiles):
        col.markdown(
            f"""<div class="tile">
                  <div class="num" style="color:{color}">{icon} {num}</div>
                  <div class="lbl">{lbl}</div>
                </div>""",
            unsafe_allow_html=True,
        )


def render_plan(plan: dict) -> None:
    render_metrics(plan["summary"])
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-h">📆 Match plan</div>', unsafe_allow_html=True)

    for a in plan["assignments"]:
        icon, color, bg, bd, label = STATUS.get(a["status"], ("•", "#333", "#eee", "#ccc", "?"))
        when = f"{a['date']} · {fmt_time(a['start_time'])}–{fmt_time(a['end_time'])}"
        who = "".join(
            f"<li>👤 {v['name']}</li>" for v in a["assigned_volunteers"]
        ) or "<li style='background:#fff;color:#94a3b8'><em>no one assigned yet</em></li>"
        gap = (
            f"<div class='gap' style='color:{color}'>⚠️ {a['gap']}</div>" if a["gap"] else ""
        )
        st.markdown(
            f"""
            <div class="shift" style="border-left:6px solid {color}; background:{bg};">
              <div class="top">
                <div>
                  <span class="title">{icon} {a['role'].title()}</span>
                  <span class="badge" style="background:{color};color:#fff;margin-left:8px">{label}</span>
                  <div class="when">{a['shift_id']} · {when}</div>
                </div>
                <div class="count" style="background:{color};color:#fff;">
                  {a['assigned_count']}/{a['min_volunteers_needed']}
                </div>
              </div>
              <ul class="who">{who}</ul>
              {gap}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_messages(output: dict) -> None:
    confirmations = output.get("confirmation_messages", [])
    broadcasts = output.get("help_needed_broadcasts", [])

    left, right = st.columns(2)
    with left:
        st.markdown(
            f'<div class="section-h">💌 Confirmations '
            f'<span class="badge" style="background:#0f766e;color:#fff">{len(confirmations)}</span></div>',
            unsafe_allow_html=True,
        )
        for c in confirmations:
            st.markdown(
                f"""<div class="msg">
                      <div class="to">To {c.get('volunteer_name')}</div>
                      <div class="meta">{c.get('email')} · shift {c.get('shift_id')}</div>
                      <div class="body">{c.get('message')}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(
            f'<div class="section-h">📣 Help-needed broadcasts '
            f'<span class="badge" style="background:#b45309;color:#fff">{len(broadcasts)}</span></div>',
            unsafe_allow_html=True,
        )
        if not broadcasts:
            st.success("Every shift is fully staffed — no broadcasts needed! 🎉")
        for b in broadcasts:
            st.markdown(
                f"""<div class="msg broadcast">
                      <div class="to">📢 Shift {b.get('shift_id')}</div>
                      <div class="body">{b.get('message')}</div>
                    </div>""",
                unsafe_allow_html=True,
            )


# --------------------------------------------------------------------------- #
# Sidebar — controls
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("### ⚙️ Run settings")

    creds_available = bool(
        os.getenv("AWS_ACCESS_KEY_ID")
        or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        or os.getenv("AWS_PROFILE")
    )
    options = ["🟢 Live agent (Strands + Bedrock)", "⚪ Offline (deterministic)"]
    default_index = 0 if creds_available else 1

    mode = st.radio(
        "Matching mode",
        options,
        index=default_index,
        help=(
            "Live agent uses the Strands Agents SDK with Amazon Bedrock to draft "
            "natural-language messages. Offline uses the deterministic matcher and "
            "template messages — no AWS credentials required (great for a public demo)."
        ),
    )
    if creds_available:
        st.success("AWS credentials detected — Live mode available.", icon="✅")
    else:
        st.info(
            "No AWS credentials — Offline is the default. This public demo runs "
            "fully without keys; Live mode falls back to Offline automatically.",
            icon="ℹ️",
        )

    # Optional bring-your-own TEMPORARY credentials (session-only, never stored).
    byo_creds: dict | None = None
    with st.expander("🔐 Test the LIVE agent with your own AWS"):
        st.caption(
            "Run the real Strands + Bedrock agent on **your own** AWS account using "
            "**temporary** credentials. Nothing is stored — usage bills to you."
        )
        st.markdown(
            "Get temporary creds via IAM Identity Center / SSO access keys, or "
            "`aws sts get-session-token --duration-seconds 3600`."
        )
        byo_key = st.text_input("AWS Access Key ID", type="password", key="byo_key")
        byo_secret = st.text_input("AWS Secret Access Key", type="password", key="byo_secret")
        byo_token = st.text_area("AWS Session Token (for temporary creds)", height=80, key="byo_token")
        byo_region = st.text_input("AWS Region", value="us-west-2", key="byo_region")
        st.caption("🔒 Session-only · never saved or logged · close the tab to clear.")
        if byo_key and byo_secret:
            byo_creds = {
                "aws_access_key_id": byo_key.strip(),
                "aws_secret_access_key": byo_secret.strip(),
                "aws_session_token": (byo_token or "").strip(),
                "region_name": (byo_region or "us-west-2").strip(),
            }
            if not byo_token.strip():
                st.warning("Temporary/STS credentials also need the session token.")

    st.divider()
    st.markdown(
        "**Built with the [Strands Agents SDK](https://strandsagents.com/).**  \n"
        "🏘️ Good Neighbor Agents · *Agents for Humans*  \n"
        "🚀 [Live demo](https://volunteer-shift-matcher.streamlit.app/)  \n"
        "📦 [GitHub repo](https://github.com/MakendranG/volunteer-shift-matcher)"
    )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
render_hero()

with st.expander("💡 What problem does this solve?"):
    st.markdown(
        "Food banks and small nonprofits chronically have unfilled volunteer shifts "
        "— not because volunteers don't exist, but because manually matching "
        "availability and skills to open shifts (via spreadsheets or group texts) is "
        "slow and error-prone for a coordinator who is already stretched thin. This "
        "agent does that matching and outreach for them."
    )

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
col_shifts, col_vols = st.columns(2)
with col_shifts:
    st.markdown('<div class="section-h">📅 Open shifts</div>', unsafe_allow_html=True)
    shifts_text = st.text_area(
        "Shifts JSON", value=load_sample("shifts.json"), height=300, label_visibility="collapsed"
    )
with col_vols:
    st.markdown('<div class="section-h">🙋 Volunteers</div>', unsafe_allow_html=True)
    vols_text = st.text_area(
        "Volunteers JSON", value=load_sample("volunteers.json"), height=300, label_visibility="collapsed"
    )

run = st.button("🚀  Match shifts", type="primary", use_container_width=True)

if run:
    try:
        shifts = json.loads(shifts_text)
        volunteers = json.loads(vols_text)
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON in the input: {exc}")
        st.stop()

    use_live = mode.startswith("🟢") or byo_creds is not None
    output = None

    if use_live:
        spinner_msg = (
            "Running the Strands agent on Amazon Bedrock with your credentials…"
            if byo_creds is not None
            else "Running the Strands agent on Amazon Bedrock…"
        )
        with st.spinner(spinner_msg):
            try:
                output = run_with_agent(shifts, volunteers, credentials=byo_creds)
            except Exception as exc:  # noqa: BLE001
                st.warning(
                    f"Live agent unavailable ({type(exc).__name__}). "
                    "Falling back to the deterministic offline matcher."
                )
                output = run_offline(shifts, volunteers)
    else:
        output = run_offline(shifts, volunteers)

    if output.get("source") == "agent":
        st.markdown(
            '<span class="badge" style="background:#16a34a;color:#fff">🟢 Live Strands agent · Amazon Bedrock</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge" style="background:#64748b;color:#fff">⚪ Offline deterministic matcher</span>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Keyless Offline mode: matching, gap detection and broadcasts are identical "
            "to the live agent — only the message wording is templated instead of "
            "LLM-drafted. The full Strands + Bedrock path runs via `python run_agent.py` "
            "and is shown in the demo video."
        )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    render_plan(output["match_plan"])
    st.divider()
    render_messages(output)
    st.divider()

    with st.expander("🧩 Structured JSON output"):
        st.json(output)
    st.download_button(
        "⬇️ Download result as JSON",
        data=json.dumps(output, indent=2),
        file_name="match_result.json",
        mime="application/json",
        use_container_width=True,
    )
else:
    st.info("Edit the inputs above (or keep the sample data) and click **🚀 Match shifts**.")
