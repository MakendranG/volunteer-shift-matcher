"""Streamlit UI for the Volunteer Shift Matcher — a Good Neighbor Agent built
with the Strands Agents SDK.

Run locally:
    streamlit run streamlit_app.py

This is a visual front-end over the SAME Strands agent used by the CLI. It lets a
volunteer coordinator paste/edit their shifts and volunteers, click one button,
and instantly see:
  - a colour-coded match plan (filled / partial / unfilled),
  - warm confirmation messages for each assigned volunteer,
  - "help needed" broadcasts for any shift that can't be filled.

Problem being solved: food banks and small nonprofits chronically have unfilled
volunteer shifts because manually matching availability/skills to open shifts is
slow and error-prone for an already-stretched coordinator.
"""

from __future__ import annotations

import json
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
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def load_sample(name: str) -> str:
    return (SAMPLE / name).read_text(encoding="utf-8")


STATUS_STYLE = {
    "filled": ("✅", "#1a7f37", "#e6f4ea"),
    "partially_filled": ("⚠️", "#9a6700", "#fff8e1"),
    "unfilled": ("❌", "#cf222e", "#fde8e8"),
}


def render_plan(plan: dict) -> None:
    s = plan["summary"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total shifts", s["total_shifts"])
    c2.metric("✅ Filled", s["filled"])
    c3.metric("⚠️ Partial", s["partially_filled"])
    c4.metric("❌ Unfilled", s["unfilled"])

    st.markdown("### Match plan")
    for a in plan["assignments"]:
        icon, color, bg = STATUS_STYLE.get(a["status"], ("•", "#333", "#eee"))
        when = f"{a['date']} · {fmt_time(a['start_time'])}–{fmt_time(a['end_time'])}"
        assigned = "".join(
            f"<li>{v['name']} &lt;{v['email']}&gt;</li>" for v in a["assigned_volunteers"]
        ) or "<li><em>no one assigned yet</em></li>"
        gap_html = (
            f"<div style='margin-top:6px;color:{color};font-weight:600'>Gap: {a['gap']}</div>"
            if a["gap"]
            else ""
        )
        st.markdown(
            f"""
            <div style="border-left:6px solid {color};background:{bg};
                        padding:12px 16px;border-radius:8px;margin-bottom:10px;">
              <div style="font-size:1.05rem;font-weight:700;">
                {icon} {a['shift_id']} · {a['role'].title()}
                <span style="font-weight:400;">— {when}</span>
                <span style="float:right;">{a['assigned_count']}/{a['min_volunteers_needed']}</span>
              </div>
              <ul style="margin:6px 0 0 0;">{assigned}</ul>
              {gap_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_messages(output: dict) -> None:
    confirmations = output.get("confirmation_messages", [])
    broadcasts = output.get("help_needed_broadcasts", [])

    left, right = st.columns(2)
    with left:
        st.markdown(f"### 💌 Confirmations ({len(confirmations)})")
        for c in confirmations:
            with st.container(border=True):
                st.markdown(
                    f"**To {c.get('volunteer_name')}** · `{c.get('shift_id')}`  \n"
                    f"<{c.get('email')}>"
                )
                st.write(c.get("message"))
    with right:
        st.markdown(f"### 📣 Help-needed broadcasts ({len(broadcasts)})")
        if not broadcasts:
            st.success("Every shift is fully staffed — no broadcasts needed! 🎉")
        for b in broadcasts:
            with st.container(border=True):
                st.markdown(f"**Shift `{b.get('shift_id')}`**")
                st.warning(b.get("message"))


# --------------------------------------------------------------------------- #
# Sidebar — controls
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("⚙️ How to run")
    mode = st.radio(
        "Matching mode",
        ["Live agent (Strands + Bedrock)", "Offline (deterministic only)"],
        help=(
            "Live agent uses the Strands Agents SDK with Amazon Bedrock to draft "
            "natural-language messages. Offline uses the deterministic matcher and "
            "template messages — no AWS credentials required (great for a demo)."
        ),
    )
    st.caption(
        "Live mode needs AWS Bedrock credentials in the environment. "
        "If it fails, the app automatically falls back to offline mode."
    )
    st.divider()
    st.markdown(
        "**Built with the [Strands Agents SDK](https://strandsagents.com/).**  \n"
        "Good Neighbor Agents track · *Agents for Humans* hackathon.  \n"
        "[GitHub repo](https://github.com/MakendranG/volunteer-shift-matcher)"
    )


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
st.title("🤝 Volunteer Shift Matcher")
st.markdown(
    "Fill a food bank's volunteer shifts in seconds. Paste your **open shifts** and "
    "**volunteers**, and the agent produces an auditable match plan, drafts warm "
    "confirmation messages, and writes *help-needed* broadcasts for any gap it "
    "can't fill."
)

with st.expander("What problem does this solve?", expanded=False):
    st.markdown(
        "Food banks and small nonprofits chronically have unfilled volunteer shifts "
        "— not because volunteers don't exist, but because manually matching "
        "availability and skills to open shifts (via spreadsheets or group texts) is "
        "slow and error-prone for a coordinator who is already stretched thin. This "
        "agent does that matching and outreach for them."
    )

col_shifts, col_vols = st.columns(2)
with col_shifts:
    st.subheader("📅 Open shifts")
    shifts_text = st.text_area(
        "Shifts JSON",
        value=load_sample("shifts.json"),
        height=320,
        label_visibility="collapsed",
    )
with col_vols:
    st.subheader("🙋 Volunteers")
    vols_text = st.text_area(
        "Volunteers JSON",
        value=load_sample("volunteers.json"),
        height=320,
        label_visibility="collapsed",
    )

run = st.button("🚀 Match shifts", type="primary", use_container_width=True)

if run:
    # Validate input JSON first with a clear error rather than a stack trace.
    try:
        shifts = json.loads(shifts_text)
        volunteers = json.loads(vols_text)
    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON in the input: {exc}")
        st.stop()

    use_live = mode.startswith("Live")
    output = None

    if use_live:
        with st.spinner("Running the Strands agent on Amazon Bedrock…"):
            try:
                output = run_with_agent(shifts, volunteers)
            except Exception as exc:  # noqa: BLE001
                st.warning(
                    f"Live agent unavailable ({type(exc).__name__}). "
                    "Falling back to the deterministic offline matcher."
                )
                output = run_offline(shifts, volunteers)
    else:
        output = run_offline(shifts, volunteers)

    badge = (
        "🟢 Live Strands agent (Bedrock)"
        if output.get("source") == "agent"
        else "⚪ Offline deterministic matcher"
    )
    st.info(f"Result generated by: **{badge}**")

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
    )
else:
    st.info("Edit the inputs above (or keep the sample data) and click **Match shifts**.")
