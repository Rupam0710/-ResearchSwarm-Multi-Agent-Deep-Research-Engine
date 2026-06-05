"""
generate_deck.py
Generates a 10-slide hackathon pitch deck PDF for ResearchSwarm.
Requirements: pip install reportlab pillow
"""

import os
import io
import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
BG        = HexColor("#0F1117")
WHITE     = HexColor("#FFFFFF")
ACCENT    = HexColor("#4F8EF7")
SECONDARY = HexColor("#A0AEC0")
DARK_GREY = HexColor("#2D3748")
MID_GREY  = HexColor("#4A5568")

PAGE_W, PAGE_H = landscape(A4)   # 841.89 x 595.28 pt
ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def bg(c: canvas.Canvas):
    """Fill slide background."""
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def watermark_and_page_num(c: canvas.Canvas, page_num: int, total: int = 10):
    """Add bottom-left watermark and bottom-right page number."""
    margin = 18
    c.setFont("Helvetica", 8)
    c.setFillColor(MID_GREY)
    c.drawString(margin, margin, "ResearchSwarm")
    c.drawRightString(PAGE_W - margin, margin, f"{page_num} / {total}")


def accent_line(c: canvas.Canvas, y: float, x_start: float = 40, width: float = 100):
    """Draw a small accent underline below a heading."""
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2.5)
    c.line(x_start, y, x_start + width, y)


def heading(c: canvas.Canvas, text: str, y: float, x: float = 40, font_size: int = 26):
    """Draw a slide section heading in accent color."""
    c.setFont("Helvetica-Bold", font_size)
    c.setFillColor(ACCENT)
    c.drawString(x, y, text)
    accent_line(c, y - 6, x, len(text) * font_size * 0.55)


def bullet_lines(
    c: canvas.Canvas,
    lines: list,
    x: float,
    y_start: float,
    line_height: float = 24,
    font_size: int = 13,
    color=None,
    max_width: float = PAGE_W - 80,
    indent: float = 0,
):
    """Draw a list of bullet strings, wrapping long lines."""
    if color is None:
        color = SECONDARY
    c.setFont("Helvetica", font_size)
    c.setFillColor(color)
    y = y_start
    for line in lines:
        # Simple wrap: split into chunks of ~max_chars characters
        max_chars = int(max_width / (font_size * 0.52))
        words = line.split(" ")
        current = ""
        first_line = True
        for word in words:
            test = (current + " " + word).strip()
            if len(test) <= max_chars:
                current = test
            else:
                draw_x = x + (indent if not first_line else 0)
                c.drawString(draw_x, y, current)
                y -= line_height
                current = word
                first_line = False
        if current:
            draw_x = x + (indent if not first_line else 0)
            c.drawString(draw_x, y, current)
            y -= line_height
    return y


def try_load_image(path_candidates: list) -> ImageReader | None:
    """Return an ImageReader for the first existing path, else None."""
    for p in path_candidates:
        p = Path(p)
        if p.exists():
            try:
                return ImageReader(str(p))
            except Exception:
                continue
    return None


def placeholder_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, label: str = ""):
    """Draw a grey placeholder rectangle with a centred label."""
    c.setFillColor(DARK_GREY)
    c.setStrokeColor(MID_GREY)
    c.setLineWidth(1)
    c.rect(x, y, w, h, fill=1, stroke=1)
    if label:
        c.setFont("Helvetica", 10)
        c.setFillColor(SECONDARY)
        c.drawCentredString(x + w / 2, y + h / 2 - 5, label)


def draw_image_or_placeholder(
    c: canvas.Canvas,
    path_candidates: list,
    x: float, y: float,
    w: float, h: float,
    label: str = "",
):
    img = try_load_image(path_candidates)
    if img:
        c.drawImage(img, x, y, width=w, height=h, preserveAspectRatio=True, anchor="c", mask="auto")
    else:
        placeholder_box(c, x, y, w, h, label or "Image not found")


# ---------------------------------------------------------------------------
# SLIDE 1 — Title
# ---------------------------------------------------------------------------
def slide_01(c: canvas.Canvas):
    bg(c)

    # Decorative accent bar left
    c.setFillColor(ACCENT)
    c.rect(0, 0, 6, PAGE_H, fill=1, stroke=0)

    # Title
    c.setFont("Helvetica-Bold", 52)
    c.setFillColor(WHITE)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 170, "ResearchSwarm")

    # Accent underline centred
    uw = 320
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.line(PAGE_W / 2 - uw / 2, PAGE_H - 185, PAGE_W / 2 + uw / 2, PAGE_H - 185)

    # Subtitle
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 225, "Multi-Agent Deep Research Engine")

    # Tagline
    c.setFont("Helvetica-Oblique", 15)
    c.setFillColor(SECONDARY)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 268,
                        '"Deeper research. Faster insights. Powered by a swarm."')

    # Hackathon badge
    badge_w, badge_h = 420, 36
    bx = PAGE_W / 2 - badge_w / 2
    by = PAGE_H - 360
    c.setFillColor(DARK_GREY)
    c.roundRect(bx, by, badge_w, badge_h, 8, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, by + 12, "Microsoft Build AI Hackathon — Agent Swarms Track")

    watermark_and_page_num(c, 1)


# ---------------------------------------------------------------------------
# SLIDE 2 — Problem Statement
# ---------------------------------------------------------------------------
def slide_02(c: canvas.Canvas):
    bg(c)

    heading(c, "The Problem", PAGE_H - 80)

    bullets = [
        "•  Researching complex topics takes hours of manual work",
        "•  Single LLM calls produce shallow, unverified answers",
        "•  No visibility into sources or reasoning",
        "•  Critical gaps and hallucinations go undetected",
        "•  Knowledge workers spend 30% of their time just gathering information",
    ]
    bullet_lines(c, bullets, x=50, y_start=PAGE_H - 140, line_height=52,
                 font_size=15, max_width=PAGE_W - 100)

    watermark_and_page_num(c, 2)


# ---------------------------------------------------------------------------
# SLIDE 3 — Solution Overview
# ---------------------------------------------------------------------------
def slide_03(c: canvas.Canvas):
    bg(c)

    heading(c, "The Solution", PAGE_H - 80)

    bullets = [
        "•  ResearchSwarm deploys a coordinated swarm of specialized AI agents",
        "•  Each agent has one job and does it in parallel",
        "•  Result: comprehensive, cited, verified research reports in minutes",
        "•  Full source transparency and real-time agent visibility",
        "•  A Critic Agent scores confidence and flags unsupported claims",
    ]
    bullet_lines(c, bullets, x=50, y_start=PAGE_H - 140, line_height=52,
                 font_size=15, max_width=PAGE_W - 100)

    watermark_and_page_num(c, 3)


# ---------------------------------------------------------------------------
# SLIDE 4 — How It Works
# ---------------------------------------------------------------------------
def slide_04(c: canvas.Canvas):
    bg(c)
    heading(c, "How It Works", PAGE_H - 80)

    steps = [
        ("🧠", "Planner",    "Breaks question\ninto sub-topics"),
        ("🔍", "Search",     "Parallel web search\nvia Tavily"),
        ("📄", "Reader",     "Extracts key insights\nfrom sources"),
        ("✍️",  "Synthesis",  "Composes structured\nreport"),
        ("✅", "Critic",     "Reviews quality,\nscores confidence"),
    ]

    n = len(steps)
    box_w = 130
    box_h = 100
    gap   = (PAGE_W - 80 - n * box_w) / (n - 1)
    y_box = PAGE_H - 260
    x_start = 40

    for i, (emoji, label, desc) in enumerate(steps):
        bx = x_start + i * (box_w + gap)

        # Box
        c.setFillColor(DARK_GREY)
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.5)
        c.roundRect(bx, y_box, box_w, box_h, 8, fill=1, stroke=1)

        # Emoji
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(WHITE)
        c.drawCentredString(bx + box_w / 2, y_box + box_h - 32, emoji)

        # Label
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(ACCENT)
        c.drawCentredString(bx + box_w / 2, y_box + box_h - 54, label)

        # Description (two lines)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(SECONDARY)
        for j, dline in enumerate(desc.split("\n")):
            c.drawCentredString(bx + box_w / 2, y_box + box_h - 72 - j * 13, dline)

        # Arrow (except after last)
        if i < n - 1:
            ax = bx + box_w + 4
            ay = y_box + box_h / 2
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1.5)
            c.line(ax, ay, ax + gap - 8, ay)
            # Arrowhead
            c.setFillColor(ACCENT)
            p = c.beginPath()
            p.moveTo(ax + gap - 8, ay)
            p.lineTo(ax + gap - 16, ay + 5)
            p.lineTo(ax + gap - 16, ay - 5)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

    watermark_and_page_num(c, 4)


# ---------------------------------------------------------------------------
# SLIDE 5 — Architecture
# ---------------------------------------------------------------------------
def slide_05(c: canvas.Canvas):
    bg(c)
    heading(c, "Architecture", PAGE_H - 80)

    svg_path = ROOT / "researchswarm_architecture.svg"

    # Try cairosvg → PNG in temp file
    img_reader = None
    if svg_path.exists():
        try:
            import cairosvg # type: ignore
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            cairosvg.svg2png(url=str(svg_path), write_to=tmp.name,
                             output_width=760, output_height=380)
            tmp.close()
            img_reader = ImageReader(tmp.name)
        except Exception:
            pass

    if img_reader:
        c.drawImage(img_reader, 40, PAGE_H - 480, width=760, height=380,
                    preserveAspectRatio=True, anchor="c")
    else:
        # Text-based architecture block diagram
        layers = [
            ("React Frontend",        "(Vite + Tailwind)"),
            ("FastAPI Backend",       "(SSE Streaming)"),
            ("LangGraph Orchestrator","(StateGraph)"),
            ("Agent Swarm",           "Planner · Search · Reader · Synthesis · Critic"),
            ("External APIs",         "Tavily Search  +  Groq LLM"),
        ]
        box_w, box_h = 500, 46
        bx = (PAGE_W - box_w) / 2
        y_top = PAGE_H - 140

        for i, (title, subtitle) in enumerate(layers):
            by = y_top - i * (box_h + 10)
            # Alternate shades
            fill_color = DARK_GREY if i % 2 == 0 else HexColor("#1A202C")
            c.setFillColor(fill_color)
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1)
            c.roundRect(bx, by, box_w, box_h, 6, fill=1, stroke=1)

            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(WHITE)
            c.drawCentredString(bx + box_w / 2, by + box_h - 20, title)

            c.setFont("Helvetica", 9.5)
            c.setFillColor(SECONDARY)
            c.drawCentredString(bx + box_w / 2, by + 8, subtitle)

            # Down-arrow connector (except after last)
            if i < len(layers) - 1:
                ax = bx + box_w / 2
                ay_top = by - 2
                ay_bot = ay_top - 8
                c.setStrokeColor(ACCENT)
                c.setLineWidth(1.5)
                c.line(ax, ay_top, ax, ay_bot)
                c.setFillColor(ACCENT)
                p = c.beginPath()
                p.moveTo(ax, ay_bot)
                p.lineTo(ax - 5, ay_bot + 7)
                p.lineTo(ax + 5, ay_bot + 7)
                p.close()
                c.drawPath(p, fill=1, stroke=0)

    watermark_and_page_num(c, 5)


# ---------------------------------------------------------------------------
# SLIDE 6 — AI Integration
# ---------------------------------------------------------------------------
def slide_06(c: canvas.Canvas):
    bg(c)
    heading(c, "AI Integration", PAGE_H - 80)

    # Left column header
    col_x_left  = 50
    col_x_right = PAGE_W / 2 + 20
    col_y_hdr   = PAGE_H - 130

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(WHITE)
    c.drawString(col_x_left,  col_y_hdr, "Models & APIs")
    c.drawString(col_x_right, col_y_hdr, "Framework & Stack")

    # Divider line
    c.setStrokeColor(MID_GREY)
    c.setLineWidth(0.8)
    c.line(PAGE_W / 2, PAGE_H - 100, PAGE_W / 2, 50)

    left_items = [
        ("Planner Agent",    "Groq Llama 3.1 8b  (fast)"),
        ("Search Agent",     "Tavily Search API"),
        ("Reader Agent",     "Groq Llama 3.1 8b  (fast)"),
        ("Synthesis Agent",  "Groq Llama 3.3 70b  (powerful)"),
        ("Critic Agent",     "Groq Llama 3.3 70b  (powerful)"),
    ]
    right_items = [
        ("Orchestration",  "LangGraph"),
        ("Parallelism",    "asyncio"),
        ("Streaming",      "FastAPI SSE"),
        ("Frontend",       "React + Vite"),
        ("Deployment",     "Render + Vercel"),
    ]

    def two_col_rows(items, x, y_start):
        y = y_start
        for label, value in items:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(ACCENT)
            c.drawString(x, y, f"• {label}:")
            c.setFont("Helvetica", 12)
            c.setFillColor(SECONDARY)
            c.drawString(x + 140, y, value)
            y -= 40
        return y

    two_col_rows(left_items,  col_x_left,  col_y_hdr - 40)
    two_col_rows(right_items, col_x_right, col_y_hdr - 40)

    watermark_and_page_num(c, 6)


# ---------------------------------------------------------------------------
# SLIDE 7 — Demo Screenshots
# ---------------------------------------------------------------------------
def slide_07(c: canvas.Canvas):
    bg(c)
    heading(c, "Live Demo", PAGE_H - 80)

    # Actual filename on disk uses hyphens; also try the space-variant from the spec
    images = [
        {
            "paths": [ROOT / "homepage.png", ROOT / "homepage.jpg"],
            "caption": "Launch Interface",
        },
        {
            "paths": [
                ROOT / "live-agents-swarm-feed.png",
                ROOT / "live-agents swarm feed.png",
            ],
            "caption": "Live Agent Feed",
        },
        {
            "paths": [ROOT / "summary-page-1.png", ROOT / "summary-page-1.jpg"],
            "caption": "Research Report",
        },
        {
            "paths": [ROOT / "summary-page-2.png", ROOT / "summary-page-2.jpg"],
            "caption": "Report Continued",
        },
    ]

    # 2 × 2 grid
    margin_x = 50
    margin_y = 55
    cols, rows = 2, 2
    gap_x, gap_y = 20, 20
    caption_h = 20
    total_w = PAGE_W - 2 * margin_x
    total_h = PAGE_H - 130 - margin_y
    cell_w = (total_w - gap_x) / cols
    cell_h = (total_h - gap_y) / rows - caption_h

    for idx, item in enumerate(images):
        col = idx % cols
        row = idx // cols
        cx = margin_x + col * (cell_w + gap_x)
        cy = (PAGE_H - 130) - row * (cell_h + gap_y + caption_h) - cell_h

        draw_image_or_placeholder(
            c,
            [str(p) for p in item["paths"]],
            cx, cy, cell_w, cell_h,
            label=item["caption"],
        )

        # Caption
        c.setFont("Helvetica", 9)
        c.setFillColor(SECONDARY)
        c.drawCentredString(cx + cell_w / 2, cy - 14, item["caption"])

    watermark_and_page_num(c, 7)


# ---------------------------------------------------------------------------
# SLIDE 8 — Key Features
# ---------------------------------------------------------------------------
def slide_08(c: canvas.Canvas):
    bg(c)
    heading(c, "Key Features", PAGE_H - 80)

    features = [
        "✅  Real-time agent progress feed",
        "✅  Parallel multi-agent execution",
        "✅  Streaming report — no waiting for full pipeline",
        "✅  Critic reviews with confidence scoring",
        "✅  Full source citations",
        "✅  Deployed and live — not just a prototype",
    ]

    y = PAGE_H - 145
    for feat in features:
        # Card background
        c.setFillColor(DARK_GREY)
        c.roundRect(40, y - 8, PAGE_W - 80, 34, 6, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(WHITE)
        c.drawString(60, y + 8, feat)
        y -= 46

    watermark_and_page_num(c, 8)


# ---------------------------------------------------------------------------
# SLIDE 9 — Impact & Use Cases
# ---------------------------------------------------------------------------
def slide_09(c: canvas.Canvas):
    bg(c)
    heading(c, "Impact & Use Cases", PAGE_H - 80)

    # Divider
    c.setStrokeColor(MID_GREY)
    c.setLineWidth(0.8)
    c.line(PAGE_W / 2, PAGE_H - 100, PAGE_W / 2, 50)

    # Left: Who benefits
    lx = 50
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(WHITE)
    c.drawString(lx, PAGE_H - 135, "Who benefits")
    accent_line(c, PAGE_H - 148, lx, 130)

    who = [
        "•  Researchers and analysts",
        "•  Journalists and writers",
        "•  Students and academics",
        "•  Business strategy teams",
    ]
    bullet_lines(c, who, x=lx, y_start=PAGE_H - 175, line_height=42,
                 font_size=14, max_width=PAGE_W / 2 - 60)

    # Right: Real-world applications
    rx = PAGE_W / 2 + 20
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(WHITE)
    c.drawString(rx, PAGE_H - 135, "Real-world applications")
    accent_line(c, PAGE_H - 148, rx, 220)

    apps = [
        "•  Competitive intelligence",
        "•  Market research",
        "•  Due diligence",
        "•  Policy research",
    ]
    bullet_lines(c, apps, x=rx, y_start=PAGE_H - 175, line_height=42,
                 font_size=14, max_width=PAGE_W / 2 - 60)

    watermark_and_page_num(c, 9)


# ---------------------------------------------------------------------------
# SLIDE 10 — Team
# ---------------------------------------------------------------------------
def slide_10(c: canvas.Canvas):
    bg(c)

    # Decorative accent bar left
    c.setFillColor(ACCENT)
    c.rect(0, 0, 6, PAGE_H, fill=1, stroke=0)

    heading(c, "The Team", PAGE_H - 80)

    details = [
        ("Participant",  "Rupam Pal"),
        ("Background",   "Full Stack Developer"),
        ("Hackathon",    "Microsoft Build AI Hackathon"),
        ("Track",        "Agent Swarms (Theme 05)"),
        ("GitHub",       "https://github.com/Rupam0710/-ResearchSwarm-Multi-Agent-Deep-Research-Engine"),
        ("Live Demo",    "https://research-swarm-multi-agent-deep-res.vercel.app/"),
    ]

    y = PAGE_H - 150
    for label, value in details:
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(ACCENT)
        c.drawString(55, y, f"{label}:")

        c.setFont("Helvetica", 13)
        c.setFillColor(WHITE)
        c.drawString(200, y, value)
        y -= 46

    watermark_and_page_num(c, 10)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build_deck(output_path: str = "ResearchSwarm_Deck.pdf"):
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    c.setTitle("ResearchSwarm — Hackathon Pitch Deck")
    c.setAuthor("ResearchSwarm")
    c.setSubject("Microsoft Build AI Hackathon — Agent Swarms Track")

    slides = [
        slide_01, slide_02, slide_03, slide_04, slide_05,
        slide_06, slide_07, slide_08, slide_09, slide_10,
    ]

    for i, slide_fn in enumerate(slides):
        slide_fn(c)
        c.showPage()

    c.save()
    print(f"Deck saved as {output_path}")


if __name__ == "__main__":
    build_deck(str(ROOT / "ResearchSwarm_Deck.pdf"))
