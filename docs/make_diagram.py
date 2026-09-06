#!/usr/bin/env python3
"""Generate a standalone architecture diagram as SVG + PNG (no browser needed).

Produces docs/architecture.svg and, if 'cairosvg' is available, docs/architecture.png.
Used to create the uploadable architecture diagram required by the Devpost form.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_SVG = HERE / "architecture.svg"

TEAL = "#0f766e"
TEAL2 = "#14b8a6"
MINT = "#ecfdf5"
INK = "#0f172a"
LINE = "#94a3b8"


def box(x, y, w, h, title, sub, fill, stroke, text_color, rx=14):
    t = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )
    cx = x + w / 2
    if sub:
        t += (
            f'<text x="{cx}" y="{y + h/2 - 6}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial, sans-serif" font-size="17" font-weight="700" '
            f'fill="{text_color}">{title}</text>'
        )
        # subtitle lines
        for i, line in enumerate(sub.split("\n")):
            t += (
                f'<text x="{cx}" y="{y + h/2 + 14 + i*15}" text-anchor="middle" '
                f'font-family="Segoe UI, Arial, sans-serif" font-size="12.5" '
                f'fill="{text_color}">{line}</text>'
            )
    else:
        t += (
            f'<text x="{cx}" y="{y + h/2 + 6}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial, sans-serif" font-size="17" font-weight="700" '
            f'fill="{text_color}">{title}</text>'
        )
    return t


def arrow(x1, y1, x2, y2, label=""):
    t = (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" '
        f'stroke-width="2.5" marker-end="url(#arrow)"/>'
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 6
        t += (
            f'<text x="{mx}" y="{my}" text-anchor="middle" '
            f'font-family="Segoe UI, Arial, sans-serif" font-size="11" '
            f'fill="#475569">{label}</text>'
        )
    return t


def build_svg() -> str:
    W, H = 1200, 675
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        '<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="5" '
        'orient="auto" markerUnits="strokeWidth">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>',
        # title
        f'<text x="40" y="46" font-family="Segoe UI, Arial, sans-serif" font-size="26" '
        f'font-weight="800" fill="{INK}">Volunteer Shift Matcher — Architecture</text>',
        f'<text x="40" y="72" font-family="Segoe UI, Arial, sans-serif" font-size="14" '
        f'fill="#475569">Built with the Strands Agents SDK · Good Neighbor Agents track</text>',
    ]

    # Inputs (left)
    parts.append(box(40, 130, 240, 80, "Volunteer data", "skills + availability", MINT, TEAL2, INK))
    parts.append(box(40, 250, 240, 80, "Shift data", "role, date, time, needed", MINT, TEAL2, INK))

    # Agent container (middle)
    parts.append(
        f'<rect x="340" y="110" width="440" height="300" rx="18" fill="#f0fdfa" '
        f'stroke="{TEAL}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    )
    parts.append(
        f'<text x="560" y="138" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" '
        f'font-size="15" font-weight="800" fill="{TEAL}">shift_matcher_agent — Strands Agents SDK</text>'
    )
    parts.append(box(370, 160, 380, 66, "Agent loop (LLM)", "", TEAL, TEAL, "#ffffff"))
    parts.append(
        box(370, 250, 380, 72, "match_shifts  @tool", "deterministic Python: eligibility,\nno double-booking, flags gaps", TEAL2, TEAL, "#ffffff")
    )
    parts.append(
        box(370, 344, 380, 56, "LLM drafting layer", "Amazon Bedrock · Claude", TEAL2, TEAL, "#ffffff")
    )
    # internal arrows
    parts.append(arrow(560, 226, 560, 250, ""))
    parts.append(arrow(560, 322, 560, 344, ""))
    # side labels for the internal flow (placed to the right, no overlap)
    parts.append(
        '<text x="766" y="242" text-anchor="start" font-family="Segoe UI, Arial, sans-serif" '
        'font-size="11" fill="#475569">calls tool</text>'
    )
    parts.append(
        '<text x="766" y="338" text-anchor="start" font-family="Segoe UI, Arial, sans-serif" '
        'font-size="11" fill="#475569">match plan</text>'
    )

    # Output (right)
    parts.append(box(840, 130, 320, 70, "Output", "structured JSON + visual summary", MINT, TEAL2, INK))
    parts.append(box(840, 250, 320, 66, "Confirmation messages", "per assigned volunteer", MINT, TEAL2, INK))
    parts.append(box(840, 344, 320, 66, "Help-needed broadcasts", "per unfilled / partial shift", MINT, TEAL2, INK))

    # cross arrows
    parts.append(arrow(280, 170, 340, 210))   # volunteer -> agent
    parts.append(arrow(280, 290, 340, 250))   # shift -> agent
    parts.append(arrow(780, 260, 840, 200))   # agent -> output
    parts.append(arrow(1000, 200, 1000, 250)) # output -> confirmations
    parts.append(arrow(1000, 316, 1000, 344)) # output -> broadcasts

    # footer note
    parts.append(
        f'<text x="40" y="640" font-family="Segoe UI, Arial, sans-serif" font-size="12.5" '
        f'fill="#64748b">Deterministic tool owns the assignments (auditable); the LLM owns the '
        f'natural-language messages. Synthetic data only; no hardcoded credentials.</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    svg = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT_SVG} ({len(svg)} bytes)")
    try:
        import cairosvg  # type: ignore

        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(HERE / "architecture.png"), scale=2.0)
        print(f"wrote {HERE / 'architecture.png'}")
    except Exception as exc:  # noqa: BLE001
        print(f"(PNG not generated: {exc}. SVG can be opened in a browser and exported.)")


if __name__ == "__main__":
    main()
