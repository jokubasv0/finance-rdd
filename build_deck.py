"""Build the eleven-slide deck (plus five backups) from the paper's numbers.

Chart-led version of the presentation: every substantive slide carries a figure
or a table drawn from out/, so the deck cannot drift from the paper. Eleven main
slides at about 6 minutes is 33 seconds each; the backups are there for question
time and are numbered separately.

Type: Cambria for display (Caladea here, identical metrics), Calibri for text
(Carlito here, identical metrics). Both are present in every Office install, so
the deck travels without carrying font files.
"""

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

OUT = Path(__file__).parent / "out"
DST = OUT / "Bonds_vs_Betting_Markets.pptx"

# ---------------------------------------------------------------- palette
INK = RGBColor(0x14, 0x1B, 0x26)
NAVY = RGBColor(0x14, 0x38, 0x5C)
NAVY_DEEP = RGBColor(0x0E, 0x24, 0x3B)
RED = RGBColor(0xA5, 0x14, 0x2E)
GREY = RGBColor(0x57, 0x61, 0x70)
MUTED = RGBColor(0x93, 0x9C, 0xAA)
BORDER = RGBColor(0xDC, 0xE2, 0xEA)
LIGHT = RGBColor(0xEE, 0xF2, 0xF7)
TINT = RGBColor(0xFB, 0xF3, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ON_DARK = RGBColor(0xC9, 0xD6, 0xE4)
ON_NAVY_MUTED = RGBColor(0x8F, 0xA8, 0xC2)
PALE_RED = RGBColor(0xF3, 0xC3, 0xC8)

DISPLAY = "Cambria"
BODY = "Calibri"

W, H = 13.333, 7.5
ML = 0.9
CW = W - 2 * ML
BASE = 6.94
SLUG = "BONDS VS. BETTING MARKETS   ·   NARVYDAS & BALOGH"

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)


# ---------------------------------------------------------------- primitives
def slide(bg=WHITE):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = bg
    return s


def box(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tf


def para(tf, text, size, colour=INK, bold=False, italic=False, first=False,
         before=0, after=0, align=PP_ALIGN.LEFT, line=None, spc=None,
         font=BODY):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(before)
    p.space_after = Pt(after)
    if line:
        p.line_spacing = line
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = colour
    if spc:
        r.font._rPr.set("spc", str(spc))
    return p


def para_runs(tf, runs, size, first=False, before=0, line=None, gap=""):
    """One paragraph assembled from (text, colour, bold) runs."""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_before = Pt(before)
    if line:
        p.line_spacing = line
    for i, (txt, colour, bold) in enumerate(runs):
        if i and gap:
            r = p.add_run()
            r.text = gap
            r.font.name = BODY
            r.font.size = Pt(size)
        r = p.add_run()
        r.text = txt
        r.font.name = BODY
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = colour
    return p


def bullet(p, char, colour, indent=0.26):
    """A real hanging bullet, so wrapped lines align under the first word."""
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(indent * 914400)))
    pPr.set("indent", str(-int(indent * 914400)))
    for tag in ("a:buClr", "a:buFont", "a:buChar"):
        for old in pPr.findall(qn(tag)):
            pPr.remove(old)
    buClr = pPr.makeelement(qn("a:buClr"), {})
    buClr.append(buClr.makeelement(qn("a:srgbClr"), {"val": str(colour)}))
    pPr.append(buClr)
    pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"}))
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": char}))


def bullets(tf, items, size=15, colour=INK, accent=RED, before=9, line=1.22,
            char="▪"):
    for i, t in enumerate(items):
        p = para(tf, t, size, colour, first=(i == 0),
                 before=(0 if i == 0 else before), line=line)
        bullet(p, char, accent)


def fill_shape(shape, colour, border=None, border_w=0.75):
    sp = shape._element
    for e in sp.findall(qn("p:style")):
        sp.remove(e)
    shape.fill.solid()
    shape.fill.fore_color.rgb = colour
    if border is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = border
        shape.line.width = Pt(border_w)


def rect(s, x, y, w, h, colour=LIGHT, border=None, border_w=0.75):
    return fill_shape(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x),
                                         Inches(y), Inches(w), Inches(h)),
                      colour, border, border_w)


def hline(s, x, y, w, colour=BORDER, h=0.008):
    return rect(s, x, y, w, h, colour)


def panel(s, x, y, w, h, fill=LIGHT, border=None, bar=None, bar_colour=RED,
          bar_w=0.055):
    sh = rect(s, x, y, w, h, fill, border)
    if bar:
        rect(s, x, y, bar_w, h, bar_colour)
    return sh


def eyebrow(s, text, y=0.46, colour=RED):
    rect(s, ML, y + 0.085, 0.085, 0.085, colour)
    tf = box(s, ML + 0.24, y, CW - 0.24, 0.3)
    para(tf, text.upper(), 10, colour, bold=True, first=True, spc=200)


def headline(s, text, size=30, y=0.78, w=CW, colour=NAVY):
    tf = box(s, ML, y, w, 1.3)
    para(tf, text, size, colour, bold=True, first=True, line=1.08, font=DISPLAY)
    return tf


def kpi(s, x, y, w, number, label, colour=NAVY, numsize=34, labsize=10.5,
        rule_top=True):
    if rule_top:
        hline(s, x, y, w, BORDER)
    tf = box(s, x, y + 0.12, w, 0.55)
    para(tf, number, numsize, colour, bold=True, first=True, line=1.0, font=DISPLAY)
    tf2 = box(s, x, y + 0.16 + numsize / 72 * 1.14, w, 0.5)
    para(tf2, label, labsize, GREY, first=True, line=1.25)


def card(s, x, y, w, h, label, body, accent=RED, tint=None, body_size=12.5,
         label_size=9, bar=True, border=BORDER, body_colour=INK,
         anchor=MSO_ANCHOR.TOP):
    panel(s, x, y, w, h, fill=(tint or WHITE), border=border, bar=accent,
          bar_colour=accent, bar_w=(0.05 if bar else 0))
    tf = box(s, x + 0.3, y + (0.17 if anchor == MSO_ANCHOR.TOP else 0),
             w - 0.55, h - (0.28 if anchor == MSO_ANCHOR.TOP else 0),
             anchor=anchor)
    para(tf, label.upper(), label_size, accent, bold=True, first=True, spc=140)
    para(tf, body, body_size, body_colour, before=5, line=1.26)


def picture(s, name, x, y, max_w, max_h, cap=None, cap_size=9.5):
    """Place a figure inside (x, y, max_w, max_h), preserving its aspect ratio."""
    path = OUT / name
    iw, ih = Image.open(path).size
    aspect = iw / ih
    w = max_w
    h = w / aspect
    if h > max_h:
        h = max_h
        w = h * aspect
    s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
    if cap:
        tf = box(s, x, y + h + 0.1, w, 0.5)
        para(tf, cap, cap_size, GREY, italic=True, first=True, line=1.3)
    return y + h


def footer(s, label):
    hline(s, ML, BASE, CW, BORDER, 0.008)
    tf = box(s, ML, BASE + 0.1, 8.4, 0.26)
    para(tf, SLUG, 8, MUTED, bold=True, first=True, spc=110)
    tf2 = box(s, W - ML - 1.0, BASE + 0.08, 1.0, 0.3)
    para(tf2, label, 8.5, GREY, bold=True, first=True, align=PP_ALIGN.RIGHT)


def num(s, x, y, w, text, size=26, colour=NAVY, caption=None, cap_size=10.5):
    """A bare number with a caption underneath, no rule."""
    tf = box(s, x, y, w, 0.5)
    para(tf, text, size, colour, bold=True, first=True, line=1.0, font=DISPLAY)
    if caption:
        tf2 = box(s, x, y + size / 72 * 1.12, w, 0.5)
        para(tf2, caption, cap_size, GREY, first=True, line=1.25)


def mpara(tf, parts, size=19, colour=NAVY, bold=True, first=True,
          font=DISPLAY, before=0, line=1.15):
    """One paragraph of display maths. parts is [(text, is_subscript), ...].

    python-pptx has no subscript API, so the run gets the DrawingML baseline
    attribute directly; -25000 is the 25 per cent drop Word and PowerPoint use.
    """
    p_ = tf.paragraphs[0] if first else tf.add_paragraph()
    p_.space_before = Pt(0 if first else before)
    p_.line_spacing = line
    for text, sub in parts:
        r = p_.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.name = font
        r.font.color.rgb = colour
        if sub:
            r.font._rPr.set("baseline", "-25000")
    return p_


# -------------------------------------------------------------------- 1 cover
s = slide(NAVY_DEEP)

tf = box(s, ML + 0.05, 1.05, 9.0, 0.3)
para(tf, "EMPIRICAL FINANCE   ·   FINAL PRESENTATION", 10.5, ON_NAVY_MUTED,
     bold=True, first=True, spc=220)

tf = box(s, ML, 1.60, 9.9, 1.9)
para(tf, "Bonds vs. Betting Markets", 48, WHITE, bold=True, first=True,
     line=1.04, font=DISPLAY)

tf = box(s, ML, 3.16, 9.9, 0.6)
para(tf, "Two clocks around Hungary's 2026 election", 24, ON_DARK, first=True,
     line=1.15)

rect(s, ML, 4.00, 2.1, 0.045, RED)

tf = box(s, ML, 4.38, 9.4, 1.0)
para(tf, "Same event, two markets, one question:\ndid either of them see it coming?",
     21, PALE_RED, italic=True, first=True, line=1.3)

hline(s, ML, 6.02, CW, RGBColor(0x2A, 0x44, 0x5E), 0.008)

tf = box(s, ML, 6.2, 8.0, 0.75)
para(tf, "Jokūbas Narvydas   ·   Levente Balogh", 14, WHITE, bold=True, first=True)
para(tf, "November 2026", 11.5, ON_NAVY_MUTED, before=5)

# -------------------------------------------------------------------- 2 fact
s = slide()
eyebrow(s, "1 · The fact")
headline(s, "One country repriced.\nThe others did not.", 30, w=5.0)

kpi(s, ML, 2.06, 4.45, "−136 bp", "Hungary's ten-year yield, 7.11% → 5.75%", RED, 36)
kpi(s, ML, 3.14, 4.45, "+24 bp", "Average of the six peers — Germany is shown "
                                 "separately", NAVY, 36)
kpi(s, ML, 4.34, 4.45, "−26 bp", "Romania — the only other faller", GREY, 36)

picture(s, "fig1_levels.png", 5.92, 1.50, 6.55, 3.42,
        cap="Hungary in dark blue, the peer average in grey. The fall opens in "
            "two steps — before the vote, and after it.")

panel(s, ML, 6.02, 5.0, 0.62, fill=LIGHT, bar=True)
tf = box(s, ML + 0.28, 6.14, 4.6, 0.45)
para(tf, "Not that yields fell — where, and when.", 13, NAVY, bold=True, first=True)

footer(s, "2 / 11")

# ---------------------------------------------------------------- 3 question
s = slide()
eyebrow(s, "2 · The question")
headline(s, "Two questions: how much, and when")

card(s, ML, 1.98, 5.55, 1.34, "01 · How much",
     "A sovereign spread is a price for risk. If the market expected the "
     "government to fall, the price of that risk should fall first.",
     body_size=12)
card(s, ML + 5.95, 1.98, 5.55, 1.34, "02 · When",
     "Governments fall on a known date. So the repricing can be timed against "
     "it — which is rare, and is the whole opportunity here.",
     body_size=12)

tf = box(s, ML, 3.62, 6.0, 0.32)
para(tf, "WHY HUNGARY", 9.5, GREY, bold=True, first=True, spc=140)

tf = box(s, ML, 3.96, 5.75, 1.85)
bullets(tf, ["A single, dated, high-salience event with a two-thirds prior.",
             "A traded contract on the exact outcome, printing daily.",
             "A bond market that prices sovereign risk continuously."],
        size=14, before=8)

panel(s, 6.95, 3.96, 5.5, 1.44, fill=LIGHT, bar=True)
tf = box(s, 7.23, 4.16, 5.0, 1.05)
para(tf, "Elections are supposed to be priced before they happen. Two thirds of "
         "this one was priced after.", 14.5, NAVY, bold=True, first=True,
     line=1.24)

tf = box(s, ML, 6.02, CW, 0.4)
para(tf, "Normally we infer beliefs from spreads. Here we observe a probability "
         "and can compare the two.", 13, GREY, italic=True, first=True)

footer(s, "3 / 11")

# ------------------------------------------------------------- 4 literature
s = slide()
eyebrow(s, "3 · The literature")
headline(s, "The sign is contested, because panels throw away what markets "
            "expected", 28)

rows = [("Block & Vaaler (2004)",
         "Sovereign spreads widen before elections, not after — 1970s–1990s, "
         "monthly data, no expectations measure."),
        ("Balding (2011)",
         "The effect is conditional on the expected result: markets price the "
         "winner, not the event."),
        ("Eichler (2014)",
         "Widening is concentrated in the campaign, and reverses on the result "
         "— but only where the outcome is close.")]
y = 2.28
for name, claim in rows:
    hline(s, ML, y - 0.12, CW, BORDER)
    tf = box(s, ML, y, 4.3, 0.55)
    para(tf, name, 15, NAVY, bold=True, first=True, font=DISPLAY)
    tf = box(s, ML + 4.5, y + 0.04, CW - 4.5, 0.9)
    para(tf, claim, 12.5, INK, first=True, line=1.24)
    y += 0.86

tf = box(s, ML, 4.98, CW, 0.35)
para(tf, "ALL THREE ESTIMATE THE EFFECT FROM THE SPREAD ALONE", 9.5, GREY,
     bold=True, first=True, spc=140)

panel(s, ML, 5.36, CW, 1.24, fill=NAVY_DEEP)
tf = box(s, ML + 0.4, 5.52, 3.6, 0.3)
para(tf, "THE GAP", 8.5, PALE_RED, bold=True, first=True, spc=160)
tf = box(s, ML + 0.4, 5.80, 5.2, 0.7)
para(tf, "Nobody has put a contract and a sovereign spread on the same daily "
         "axis around a European election.", 12.5, ON_DARK, first=True, line=1.22)

tf = box(s, ML + 5.9, 5.52, 3.6, 0.3)
para(tf, "OUR CONTRIBUTION", 8.5, ON_NAVY_MUTED, bold=True, first=True, spc=160)
tf = box(s, ML + 5.9, 5.80, 5.25, 0.7)
para(tf, "That joint measurement, which is what lets the timing question be "
         "asked at all.", 12.5, WHITE, first=True, line=1.22)

footer(s, "4 / 11")

# ------------------------------------------------------------------ 5 design
s = slide()
eyebrow(s, "4 · Design")
headline(s, "Five countries, one date, and a trend fitted before it")

panel(s, ML, 1.98, CW, 0.78, fill=LIGHT)
tf = box(s, ML + 0.35, 2.10, CW - 0.7, 0.58)
mpara(tf, [("y", 0), ("it", 1), ("  =  ", 0), ("α", 0), ("i", 1), ("  +  ", 0),
           ("λ", 0), ("t", 1), ("  +  ", 0), ("β", 0), (" (", 0), ("HU", 0),
           ("i", 1), (" × ", 0), ("Post", 0), ("t", 1), (")  +  ", 0),
           ("γ", 0), ("i", 1), (" · min(", 0), ("t", 0), (",  ", 0), ("t", 0),
           ("cut", 1), (")  +  ", 0), ("ε", 0), ("it", 1)], 19)

tf = box(s, ML, 2.86, CW, 0.62)
para(tf, "Country effects absorb level differences. Date effects absorb "
         "everything common to the region on a given day.", 12, GREY, first=True)
para(tf, "Treatment switches on 13 April 2026, the first trading day after the "
         "vote, and the trend kinks at the same date.", 12, GREY, first=False,
     before=3)

x = ML
for label, value, hot in [("No trend", "−1.039", False),
                          ("Kinked trend", "−1.090", True),
                          ("Linear trend", "−1.091", False)]:
    panel(s, x, 3.62, 3.55, 0.98, fill=(TINT if hot else WHITE), border=BORDER,
          bar=(RED if hot else None))
    tf = box(s, x + 0.26, 3.74, 3.0, 0.28)
    para(tf, label.upper(), 8.5, (RED if hot else GREY), bold=True, first=True,
         spc=140)
    tf = box(s, x + 0.26, 3.98, 3.0, 0.5)
    para(tf, value, 22, NAVY, bold=True, first=True, font=DISPLAY)
    x += 3.99

tf = box(s, ML, 4.78, CW, 0.4)
para(tf, "Five basis points apart. On the 2022 sample they span 63 — which is "
         "why 2022 is not used.", 13, INK, first=True)

tf = box(s, ML, 5.32, 6.4, 1.4)
para(tf, "SAMPLE", 9.5, GREY, bold=True, first=True, spc=140)
para(tf, "Hungary, Czechia, Germany, Poland, Romania", 12, INK, before=5,
     line=1.3)
para(tf, "1 January 2024 to 8 May 2026 · 3,200 country-days", 12, INK, before=2,
     line=1.3)
para(tf, "Driscoll–Kraay t = −11.3. With one treated country that statistic is "
         "not the binding one; the randomisation inference on slide 9 is.",
     11, GREY, before=6, line=1.3)

panel(s, 7.6, 5.26, 4.85, 1.02, fill=LIGHT, bar=True)
tf = box(s, 7.88, 5.42, 4.35, 0.72)
para(tf, "Identification comes from one country diverging at one date, not from "
         "the size of the sample.", 12.5, NAVY, bold=True, first=True, line=1.24)

footer(s, "5 / 11")

# --------------------------------------------------------------- 6 magnitude
s = slide()
eyebrow(s, "5 · Result — how much")
headline(s, "160 basis points, and it is not a global move", 29)

picture(s, "fig2_spread.png", ML, 1.88, 7.1, 3.9,
        cap="Hungary's spread over three different benchmarks, in basis points. "
            "All three fall by between 160 and 187.")

tf = box(s, 8.4, 1.92, 4.1, 0.3)
para(tf, "SPREAD, 2025 → 2026", 9.5, GREY, bold=True, first=True, spc=140)
num(s, 8.4, 2.22, 4.1, "−160 bp", 26, RED, "over the six-peer average")
num(s, 8.4, 3.12, 4.1, "−174 bp", 26, NAVY, "over German Bunds")
num(s, 8.4, 4.02, 4.1, "−187 bp", 26, NAVY, "over Czechia")

panel(s, 8.4, 5.02, 4.05, 1.46, fill=LIGHT, bar=True)
tf = box(s, 8.68, 5.18, 3.55, 1.2)
para(tf, "THE CONTROLLED NUMBER", 8.5, RED, bold=True, first=True, spc=140)
para(tf, "Difference-in-differences gives −109 bp over the election window — "
         "smaller, because it also strips the common trend.", 11.5, INK,
     before=5, line=1.26)

footer(s, "6 / 11")

# ------------------------------------------------------------------ 7 timing
s = slide()
eyebrow(s, "6 · Result — when")
headline(s, "Two thirds of it came after the vote", 29)

picture(s, "deck_timing.png", ML, 1.88, 6.9, 3.55)

kpi(s, 7.75, 1.96, 4.7, "59 bp", "before the vote — 37% of the total",
    NAVY, 32)
kpi(s, 7.75, 3.02, 4.7, "102 bp", "between the result and the inauguration — "
                                 "63%", RED, 32)

panel(s, 7.75, 4.42, 4.7, 1.62, fill=LIGHT, bar=True)
tf = box(s, 8.03, 4.58, 4.15, 1.35)
para(tf, "NOT A RATE-CUT STORY", 8.5, RED, bold=True, first=True, spc=140)
para_runs(tf, [("10Y −38 bp", RED, True), ("     5Y −8 bp", NAVY, True),
               ("     HUF +11%", GREY, True)], 12, before=6, gap="")
para(tf, "The long end fell five times as far as the front end, and the forint "
         "appreciated. That is a term-premium move, not easing.", 11.5, INK,
     before=4, line=1.24)

tf = box(s, ML, 5.86, 6.9, 0.6)
para(tf, "The repricing is dated: it happens where an election result arrives, "
         "not where a central bank meets.", 12, GREY, italic=True, first=True,
     line=1.28)

footer(s, "7 / 11")

# -------------------------------------------------------------- 8 two clocks
s = slide()
eyebrow(s, "7 · The second result")
headline(s, "Different clocks", 29)

picture(s, "fig6_implied.png", ML, 1.80, 6.5, 3.5)

tf = box(s, 7.6, 1.86, 4.7, 0.3)
para(tf, "SHARE OF ITS OWN MOVE DONE", 9.5, GREY, bold=True, first=True, spc=140)

hdr_y = 2.20
tf = box(s, 7.6, hdr_y, 1.25, 0.28)
para(tf, "Date", 8.5, MUTED, bold=True, first=True, spc=100)
tf = box(s, 8.72, hdr_y, 1.15, 0.28)
para(tf, "Spread", 8.5, MUTED, bold=True, first=True, align=PP_ALIGN.RIGHT,
     spc=100)
tf = box(s, 9.95, hdr_y, 1.1, 0.28)
para(tf, "Contract", 8.5, MUTED, bold=True, first=True, align=PP_ALIGN.RIGHT,
     spc=100)
hline(s, 7.6, hdr_y + 0.28, 4.72, BORDER)

table = [("4 Aug", "0.00", "0.00", False),
         ("26 Feb", "0.26", "0.00", False),
         ("31 Mar", "0.15", "0.08", False),
         ("9 Apr", "0.37", "0.16", True),
         ("12 Apr", "0.44", "0.16", False),
         ("8 May", "1.00", "1.00", False)]
y = hdr_y + 0.38
for date, spread, contract, hot in table:
    if hot:
        rect(s, 7.5, y - 0.05, 4.92, 0.33, TINT)
        rect(s, 7.5, y - 0.05, 0.045, 0.33, RED)
    tf = box(s, 7.6, y, 1.3, 0.28)
    para(tf, date, 10.5, (RED if hot else INK), bold=hot, first=True)
    tf = box(s, 8.95, y, 1.0, 0.28)
    para(tf, spread, 10.5, INK, bold=hot, first=True, align=PP_ALIGN.RIGHT)
    tf = box(s, 10.05, y, 1.0, 0.28)
    para(tf, contract, 10.5, INK, bold=hot, first=True, align=PP_ALIGN.RIGHT)
    y += 0.34

tf = box(s, 7.6, 4.50, 4.7, 1.0)
para(tf, "Both series are rescaled to zero on 4 August and one on 8 May, so the "
         "table measures how fast each market moved, not what it believed.",
     11, GREY, first=True, line=1.26)

panel(s, 7.6, 5.42, 4.72, 1.16, fill=NAVY_DEEP)
tf = box(s, 7.88, 5.58, 4.2, 0.9)
para(tf, "Move the start back ten days and the ranking reverses. The divergence "
         "in timing is the finding; the ranking is not.", 12, WHITE, bold=True,
     first=True, line=1.24)

tf = box(s, ML, 5.62, 6.4, 0.9)
para(tf, "Through the campaign the spread did a third of its eventual move; the "
         "contract did nothing until the count, despite eight months of prints.",
     12, NAVY, bold=True, first=True, line=1.28)

footer(s, "8 / 11")

# ------------------------------------------------------------------- 9 trust
s = slide()
eyebrow(s, "8 · Can we trust it")
headline(s, "Four checks. One nearly kills the design.", 29)

checks = [("Pre-trend", "Leads oscillate, mean +0.07 — but jointly non-zero, "
                        "so the trend control is doing real work.", False),
          ("Fake election dates", "On a panel cut before the event: about zero.",
           False),
          ("Every country in turn", "Hungary −0.97. The next is +0.44.", False),
          ("The ceiling", "p = 0.125 — the floor with eight units.", True)]
y = 1.80
for name, claim, hot in checks:
    card(s, ML, y, 5.4, 1.12, name, claim,
         accent=(RED if hot else NAVY), tint=(TINT if hot else None),
         body_size=11.5 if hot is False else 11.5)
    y += 1.22

picture(s, "fig7_event_study.png", 6.45, 1.78, 6.0, 3.1,
        cap="Monthly coefficients against February 2026. The break is after the "
            "vote, not before it.")

card(s, 6.45, 5.28, 5.98, 1.02, "Alternative estimator",
     "Intensity (Hungary × P): −1.13, four basis points from the binary — on a "
     "panel a third the size.", accent=NAVY, body_size=11.5)

footer(s, "9 / 11")

# -------------------------------------------------------------- 10 what kills
s = slide()
eyebrow(s, "9 · What would kill it")
headline(s, "Three things could take this apart", 29)

picture(s, "fig4_spread_path.png", ML, 1.84, 6.5, 3.4)

tf = box(s, ML, 5.34, 6.4, 0.9)
para(tf, "Hungary minus Czechia, Poland and Romania, 2022–2026. From 250 basis "
         "points in 2022 to under 150 in 2024: a downward trend of its own, which "
         "is why the 2022 sample cannot be used.", 11.5, GREY, italic=True,
     first=True, line=1.26)

card(s, 7.75, 1.78, 4.7, 1.44, "One treated country",
     "Inference has one unit of treatment variation. Randomisation inference is "
     "the honest bound, and it floors at 1/8.", body_size=11.5)
card(s, 7.75, 3.32, 4.7, 1.44, "A pre-trend only a trend absorbs",
     "Leads are jointly non-zero. Without the kinked control the estimate is "
     "−1.04; the trend is not decoration.", body_size=11.5)
card(s, 7.75, 4.86, 4.7, 1.44, "Where the clock starts",
     "The share comparison reverses between two start dates ten days apart, so "
     "no claim about leadership survives.", body_size=11.5)

footer(s, "10 / 11")

# -------------------------------------------------------------- 11 takeaways
s = slide()
eyebrow(s, "10 · Takeaways")
headline(s, "What the paper argues", 30)

kpi(s, ML, 2.06, 3.62, "−160 bp", "Hungary's spread over six peers", RED, 36)
kpi(s, ML + 3.95, 2.06, 3.62, "63%", "of it came after the result", RED, 36)
kpi(s, ML + 7.9, 2.06, 3.62, "37%", "of it was done by 9 April, three days out",
    NAVY, 36)

tf = box(s, ML, 3.66, 11.2, 1.1)
para(tf, "Hungarian sovereign risk fell about 160 basis points relative to its "
         "neighbours, almost all of it at the long end, and nearly two thirds of "
         "it after the result was known.", 16.5, INK, first=True, line=1.3)

panel(s, ML, 4.94, CW, 1.42, fill=NAVY_DEEP)
tf = box(s, ML + 0.42, 5.14, 3.3, 0.3)
para(tf, "CONDITIONAL", 8.5, ON_NAVY_MUTED, bold=True, first=True, spc=160)
tf = box(s, ML + 0.42, 5.44, 10.4, 0.8)
para(tf, "One treated country, a pre-trend only a trend control absorbs, and a "
         "p-value floored at one in eight. The magnitudes are robust; the timing "
         "ranking is not.", 13.5, WHITE, bold=True, first=True, line=1.26)

tf = box(s, ML, 6.52, 11.2, 0.35)
para(tf, "Thank you.", 12, GREY, italic=True, first=True)

footer(s, "11 / 11")

# ---------------------------------------------------------------- B1 residual
s = slide()
eyebrow(s, "Backup · B1")
headline(s, "The move is Hungary-specific once the region is controlled", 26)

picture(s, "fig3_residual.png", ML, 1.86, 7.0, 3.9,
        cap="Cumulative residual from a market model on regional, US, VIX and "
            "Brent changes. It drifts down before the vote and falls after it.")

tf = box(s, 8.35, 1.94, 4.1, 0.3)
para(tf, "MARKET MODEL", 9.5, GREY, bold=True, first=True, spc=140)
tf = box(s, 8.35, 2.24, 4.1, 1.8)
para(tf, "N = 841 · R² = 0.248", 12, INK, first=True)
para(tf, "Regional beta 0.916 (t 8.43)", 11.5, INK, before=4)
para(tf, "US ten-year 0.129 (t 1.65)", 11.5, INK, before=3)
para(tf, "VIX 0.0011 (t 0.37)", 11.5, INK, before=3)
para(tf, "Brent 0.109 (t 0.48)", 11.5, INK, before=3)

panel(s, 8.35, 4.36, 4.05, 1.1, fill=LIGHT, bar=True)
tf = box(s, 8.63, 4.52, 3.55, 0.85)
para(tf, "Cumulative residual −182 bp by 8 May: the fall is not the region "
         "falling.", 11.5, NAVY, bold=True, first=True, line=1.24)

footer(s, "B1")

# ------------------------------------------------------------- B2 main table
s = slide()
eyebrow(s, "Backup · B2")
headline(s, "The estimates, side by side", 27)

rows = [("", "β", "se", "t", "N"),
        ("Kinked trend (headline)", "−1.090", "0.096", "−11.32", "3,200"),
        ("No trend", "−1.039", "0.089", "−11.61", "3,200"),
        ("Linear trend", "−1.091", "0.096", "−11.34", "3,200"),
        ("Intensity, Hungary × P", "−1.128", "0.073", "−15.55", "1,000"),
        ("Eight-country panel", "−0.965", "—", "—", "1,960")]
xcol = [ML, ML + 5.8, ML + 7.2, ML + 8.4, ML + 9.8]
for i, r in enumerate(rows):
    y = 1.94 + i * 0.56
    if i == 0:
        hline(s, ML, y - 0.10, CW, BORDER)
        for j, cell in enumerate(r):
            tf = box(s, xcol[j], y, 1.4, 0.3)
            para(tf, cell, 9.5, MUTED, bold=True, first=True, spc=100)
    else:
        for j, cell in enumerate(r):
            tf = box(s, xcol[j], y, 5.4 if j == 0 else 1.2, 0.3)
            para(tf, cell, (12.5 if j == 0 else 12),
                 (NAVY if j == 1 else INK), bold=(j == 0 or j == 1),
                 first=True, font=(BODY if j == 0 else DISPLAY))
    hline(s, ML, y + 0.40, CW, BORDER)

tf = box(s, ML, 5.18, 11.2, 1.0)
para(tf, "Driscoll–Kraay standard errors, bandwidth 10. The intensity design "
         "uses only the ten months where the contract exists, which is why it "
         "has a third of the observations and a larger t.", 11.5, GREY, italic=True,
     first=True, line=1.28)

footer(s, "B2")

# ------------------------------------------------------------ B3 placebos
s = slide()
eyebrow(s, "Backup · B3")
headline(s, "Every country in turn, as if it were Hungary", 27)

picture(s, "fig8_placebo_did.png", ML, 1.86, 7.0, 3.9,
        cap="The same specification applied to each peer. Hungary is the only "
            "large negative estimate.")

tf = box(s, 8.35, 1.94, 4.1, 0.3)
para(tf, "COEFFICIENT BY UNIT", 9.5, GREY, bold=True, first=True, spc=140)
vals = [("Hungary", "−0.97", RED), ("Romania", "+0.44", INK),
        ("Poland", "+0.27", INK), ("Slovenia", "+0.16", INK),
        ("Austria", "+0.04", INK), ("Czechia", "+0.02", INK),
        ("Germany", "+0.02", INK), ("Croatia", "0.00", INK)]
y = 2.28
for name, v, c in vals:
    tf = box(s, 8.35, y, 2.6, 0.28)
    para(tf, name, 11.5, INK, first=True)
    tf = box(s, 10.85, y, 1.2, 0.28)
    para(tf, v, 11.5, c, bold=(c == RED), first=True, align=PP_ALIGN.RIGHT,
         font=DISPLAY)
    y += 0.38

panel(s, 8.35, 5.62, 4.05, 0.94, fill=LIGHT, bar=True)
tf = box(s, 8.63, 5.78, 3.55, 0.7)
para(tf, "Randomisation inference: p = 0.125, the floor with eight units.",
     11.5, NAVY, bold=True, first=True, line=1.24)

footer(s, "B3")

# -------------------------------------------------------------- B4 base date
s = slide()
eyebrow(s, "Backup · B4")
headline(s, "Where the clock starts decides who looks ahead", 27)

rows = [("Base date", "Spread", "P", "Spread, share", "Contract, share"),
        ("25 Jul 2025", "2.74", "0.385", "0.35", "0.49"),
        ("4 Aug 2025", "2.76", "0.625", "0.37", "0.16"),
        ("11 Aug 2025", "2.64", "0.575", "0.31", "0.26"),
        ("1 Sep 2025", "2.75", "0.605", "0.36", "0.20"),
        ("1 Oct 2025", "2.49", "0.600", "0.23", "0.21"),
        ("3 Nov 2025", "2.58", "0.565", "0.29", "0.28")]
xcol = [ML, ML + 3.3, ML + 5.1, ML + 6.9, ML + 9.0]
for i, r in enumerate(rows):
    y = 1.98 + i * 0.52
    for j, cell in enumerate(r):
        tf = box(s, xcol[j], y, 2.0, 0.3)
        para(tf, cell, (12.5 if i else 9.5),
             (MUTED if i == 0 else INK), bold=(i == 0 or j == 0), first=True,
             spc=(100 if i == 0 else None),
             font=(BODY if i == 0 else DISPLAY if j else BODY))
    if i == 0:
        hline(s, ML, y - 0.08, CW, BORDER)
        y_top = y
    hline(s, ML, y + 0.36, CW, BORDER)

tf = box(s, ML, 5.44, 11.2, 1.1)
para(tf, "Each row normalises both series on its own base date, so both are zero "
         "there and one on 8 May 2026. The spread's share stays between 23 and 37 "
         "per cent; the contract's ranges from 16 to 49, because almost all of its "
         "early movement was in its first week. The 4 August row is the window's "
         "own base date and the one Figure 6 plots.", 11.5, GREY, italic=True,
     first=True, line=1.28)

footer(s, "B4")

# ------------------------------------------------------------ B5 term structure
s = slide()
eyebrow(s, "Backup · B5")
headline(s, "The curve flattens: a long-end story", 27)

picture(s, "fig5_slope.png", ML, 1.86, 7.0, 3.9,
        cap="Ten-year minus five-year slope, January to May 2026.")

tf = box(s, 8.35, 1.94, 4.1, 0.3)
para(tf, "PRE-VOTE, 4 AUG → 9 APR", 9.5, GREY, bold=True, first=True, spc=140)
num(s, 8.35, 2.26, 4.1, "−38 bp", 24, NAVY, "ten-year")
num(s, 8.35, 3.10, 4.1, "−8 bp", 24, NAVY, "five-year")
num(s, 8.35, 3.94, 4.1, "−30 bp", 24, RED, "slope, +35 → +5")

panel(s, 8.35, 5.02, 4.05, 1.28, fill=LIGHT, bar=True)
tf = box(s, 8.63, 5.18, 3.55, 1.0)
para(tf, "Easing moves the short end first. Here the long end fell five times as "
         "far, so this is term premium, not policy.", 11.5, NAVY, bold=True,
     first=True, line=1.24)

footer(s, "B5")

# ---------------------------------------------------------------- validation
bad = []
for i, sl in enumerate(prs.slides, start=1):
    for sh in sl.shapes:
        x0, y0 = sh.left / 914400, sh.top / 914400
        x1 = x0 + sh.width / 914400
        y1 = y0 + sh.height / 914400
        if x0 < -0.02 or y0 < -0.02 or x1 > W + 0.02 or y1 > H + 0.02:
            bad.append(f"slide {i}: {sh.shape_type} at "
                       f"({x0:.2f}, {y0:.2f}) extends to ({x1:.2f}, {y1:.2f})")
if bad:
    raise SystemExit("\n".join(bad))

prs.save(str(DST))
print(f"wrote {DST}  ({len(prs.slides)} slides, bounds checked)")
