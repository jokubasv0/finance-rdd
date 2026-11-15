"""Build the presentation deck from the paper's numbers and figures.

Eight slides, 16:9, matching out/talk.md slide for slide. Figures are read
from out/, so the deck cannot drift from the paper. Every shape is bounds
checked against the slide before saving.
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
DST = OUT / "Pricing_Regime_Change.pptx"

NAVY = RGBColor(0x1F, 0x4E, 0x79)
RED = RGBColor(0xC0, 0x00, 0x00)
GREY = RGBColor(0x6B, 0x72, 0x80)
MUTED = RGBColor(0x9A, 0xA1, 0xAC)
LIGHT = RGBColor(0xE9, 0xEE, 0xF4)
INK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Arial"      # Arial metrics everywhere: Liberation Sans here, Arial elsewhere
W, H = 13.333, 7.5
ML = 0.85
CW = W - 2 * ML

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)


# ---------------------------------------------------------------- primitives
def slide():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = WHITE
    return s


def box(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tf


def para(tf, text, size, colour=INK, bold=False, italic=False, first=False,
         before=0, after=0, align=PP_ALIGN.LEFT, line=None, spc=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(before)
    p.space_after = Pt(after)
    if line:
        p.line_spacing = line
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = colour
    if spc:
        r.font._rPr.set("spc", str(spc))
    return p


def solid(shape, colour):
    """Fill a shape and strip the theme style that would add a drop shadow."""
    sp = shape._element
    for e in sp.findall(qn("p:style")):
        sp.remove(e)
    shape.fill.solid()
    shape.fill.fore_color.rgb = colour
    shape.line.fill.background()


def rule(s, x, y, w, colour=NAVY, h=0.03):
    solid(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                             Inches(w), Inches(h)), colour)


def band(s, x, y, w, h, colour=LIGHT):
    solid(s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                             Inches(w), Inches(h)), colour)


def eyebrow(s, text):
    tf = box(s, ML, 0.5, CW, 0.3)
    para(tf, text.upper(), 11, GREY, bold=True, first=True, spc=170)


def headline(s, text, size=32, y=0.9, w=CW, colour=INK):
    tf = box(s, ML, y, w, 1.6)
    para(tf, text, size, colour, bold=True, first=True, line=1.05)
    return tf


def kpi(s, x, y, w, number, label, colour=NAVY, numsize=34, labsize=11):
    tf = box(s, x, y, w, 0.62)
    para(tf, number, numsize, colour, bold=True, first=True)
    tf2 = box(s, x, y + 0.56, w, 0.5)
    para(tf2, label, labsize, GREY, first=True, line=1.2)


def picture(s, name, x, y, max_w, max_h, cap=None):
    """Place a figure inside (x, y, max_w, max_h), preserving its aspect ratio."""
    path = OUT / name
    iw, ih = Image.open(path).size
    aspect = iw / ih
    w = max_w
    h = w / aspect
    if h > max_h:                      # height limited
        h = max_h
        w = h * aspect
    s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
    if cap:
        tf = box(s, x, y + h + 0.12, w, 0.55)
        para(tf, cap, 10.5, GREY, italic=True, first=True, line=1.2)
    return y + h


def footer(s, n):
    tf = box(s, ML, 7.02, 7.0, 0.28)
    para(tf, "Pricing Regime Change  ·  Narvydas & Balogh", 9, MUTED, first=True)
    tf2 = box(s, W - ML - 0.8, 7.02, 0.8, 0.28)
    para(tf2, str(n), 9, MUTED, first=True, align=PP_ALIGN.RIGHT)


# -------------------------------------------------------------------- slide 1
s = slide()
band(s, 0, 0, 0.38, H, NAVY)

tf = box(s, 1.2, 1.5, 10.6, 0.3)
para(tf, "EMPIRICAL FINANCE", 12, GREY, bold=True, first=True, spc=250)

tf = box(s, 1.2, 1.98, 11.0, 2.2)
para(tf, "Pricing Regime Change", 50, NAVY, bold=True, first=True, line=1.0)
para(tf, "Hungary's 2026 election and sovereign risk", 28, INK, before=8, line=1.1)

rule(s, 1.2, 4.1, 2.4, RED, 0.045)

tf = box(s, 1.2, 4.42, 10.4, 0.7)
para(tf, "Did markets price the fall of a government before it fell?",
     20, RED, italic=True, first=True, line=1.2)

tf = box(s, 1.2, 6.0, 10.6, 0.8)
para(tf, "Jokūbas Narvydas   ·   Levente Balogh", 15, INK, bold=True, first=True)
para(tf, "November 2026", 13, GREY, before=4)

# -------------------------------------------------------------------- slide 2
s = slide()
eyebrow(s, "Data and the fact")
headline(s, "Hungary's yield fell.\nEvery neighbour's rose.", 30, y=0.88, w=5.2)

kpi(s, ML, 2.55, 4.6, "−138 bp", "Hungary's ten-year yield, 7.13% → 5.75%", RED, 36)
kpi(s, ML, 3.72, 4.6, "+19 bp", "Six-peer average", NAVY, 36)
kpi(s, ML, 4.89, 4.6, "−21 bp", "Romania — the only other fall, and less than a sixth as large", GREY, 36)

picture(s, "fig1_levels.png", 6.25, 1.72, 6.3, 3.35,
        cap="Hungary in dark blue, the peer average in grey. The fall opens in two "
            "steps — before the vote, and after it.")

tf = box(s, ML, 5.98, CW, 0.6)
para(tf, "That shape is the whole paper: not that yields fell, but where and when.",
     17, NAVY, bold=True, first=True, line=1.2)
footer(s, 2)

# -------------------------------------------------------------------- slide 3
s = slide()
eyebrow(s, "The question")
headline(s, "Two questions: how much, and when")

for i, (label, text) in enumerate([
        ("HOW MUCH", "Did the risk premium really reprice around the vote?"),
        ("WHEN", "Before the result — or only after it?")]):
    x = ML + i * 6.0
    rule(s, x, 2.18, 5.3, LIGHT, 0.03)
    tf = box(s, x, 2.38, 5.3, 1.5)
    para(tf, label, 10, GREY, bold=True, first=True, spc=170)
    para(tf, text, 19, NAVY, bold=True, before=8, line=1.25)

tf = box(s, ML, 4.28, 11.6, 1.7)
para(tf, "WHY HUNGARY", 10, GREY, bold=True, first=True, spc=170)
for t in ["Sixteen years of one government — regime risk, not a routine rotation",
          "EU funds frozen — the result carried a fiscal consequence",
          "A prediction market on the exact event, printing daily for ten months"]:
    para(tf, t, 15, INK, before=7, line=1.15)

tf = box(s, ML, 6.05, 11.6, 0.4)
para(tf, "Normally we infer beliefs from spreads. Here we observe a probability.",
     13, RED, italic=True, first=True)
footer(s, 3)

# -------------------------------------------------------------------- slide 4
s = slide()
eyebrow(s, "The literature")
headline(s, "The sign is contested, because panels\nthrow away what markets expected", 29,
         y=0.88)

y = 2.5
for name, claim in [("Block & Vaaler 2004", "Sovereign spreads fall into the vote"),
                    ("Balding 2011", "Daily CDS: they rise"),
                    ("Eichler 2014", "Nothing, once governance is controlled")]:
    rule(s, ML, y, CW, LIGHT, 0.025)
    tf = box(s, ML, y + 0.13, 4.4, 0.4)
    para(tf, name, 16, NAVY, bold=True, first=True)
    tf = box(s, ML + 4.5, y + 0.13, 7.1, 0.4)
    para(tf, claim, 16, INK, first=True)
    y += 0.74

tf = box(s, ML, 4.78, CW, 0.7)
para(tf, "A panel averages over events. The expectation that made each event "
         "matter is the one thing it discards.", 15, INK, first=True, line=1.25)

band(s, ML, 5.42, CW, 1.18)
tf = box(s, ML + 0.4, 5.54, CW - 0.8, 0.98, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "THE GAP   Nobody has put a contract and a sovereign spread on the same "
         "daily axis around a European election.", 15, NAVY, bold=True, first=True,
     line=1.2)
para(tf, "OUR CONTRIBUTION   That joint daily measurement, which is what lets the "
         "timing question be asked at all.", 14, INK, before=7, line=1.2)
footer(s, 4)

# -------------------------------------------------------------------- slide 5
s = slide()
eyebrow(s, "Identification")
headline(s, "Difference-in-differences against\nneighbouring markets", 30, y=0.86)

tf = box(s, ML, 2.34, CW, 0.45)
para(tf, "yᵢₜ = αᵢ + λₜ + β(HUᵢ × Postₜ) + γᵢ · min(t, t_cut) + εᵢₜ", 21, NAVY,
     first=True)
tf = box(s, ML, 2.95, CW, 0.4)
para(tf, "country effects  ·  date effects  ·  a country trend fitted before the "
         "vote and held flat after it", 12, GREY, first=True)

kpi(s, ML, 3.62, 3.4, "−1.04", "no trend", NAVY, 38)
kpi(s, ML + 3.7, 3.62, 3.4, "−1.09", "kinked trend — the headline", RED, 38)
kpi(s, ML + 7.4, 3.62, 3.4, "−1.09", "linear trend", NAVY, 38)

tf = box(s, ML, 4.92, CW, 0.5)
para(tf, "Five basis points apart.", 20, INK, bold=True, first=True)

tf = box(s, ML, 5.55, 9.4, 1.3)
para(tf, "On a sample reaching back to 2022 the same three specifications span "
         "sixty-three basis points, because the 2022 disinflation is "
         "indistinguishable from an election effect. That is why the sample "
         "starts in 2024 — a test, not a preference.", 13, GREY, first=True,
     line=1.35)

tf = box(s, 10.55, 5.58, 2.0, 0.9)
para(tf, "t = −11.3", 13, INK, bold=True, first=True, align=PP_ALIGN.RIGHT)
para(tf, "N = 3,200", 12, GREY, before=5, align=PP_ALIGN.RIGHT)
para(tf, "2024–2026", 12, GREY, before=4, align=PP_ALIGN.RIGHT)
footer(s, 5)

# -------------------------------------------------------------------- slide 6
s = slide()
eyebrow(s, "Robustness")
headline(s, "Four checks. One nearly\nkills the design.", 29, y=0.86, w=5.4)

y = 2.42
for name, claim in [("Pre-trend", "Leads oscillate, they do not trend. Mean +0.07."),
                    ("Fake election dates", "On a panel cut before the event: ≈ 0."),
                    ("Every country in turn", "Hungary −0.97. The next is +0.44."),
                    ("The ceiling", "p = 0.125 — the floor with eight units.")]:
    tf = box(s, ML, y, 5.2, 0.95)
    para(tf, name.upper(), 9.5, GREY, bold=True, first=True, spc=150)
    para(tf, claim, 13.5, INK, before=4, line=1.25)
    y += 1.07

picture(s, "fig7_event_study.png", 6.4, 1.85, 6.3, 3.2,
        cap="Pre-treatment leads oscillate around zero; the break lands after "
            "the vote, not before it.")
footer(s, 6)

# -------------------------------------------------------------------- slide 7
s = slide()
eyebrow(s, "What fails")
headline(s, "What fails, and what surprised us", 30, y=0.88)

tf = box(s, ML, 2.28, 4.9, 1.5)
para(tf, "DAILY DESIGN", 9.5, GREY, bold=True, first=True, spc=150)
para(tf, "β ≈ 0", 34, MUTED, bold=True, before=2)
para(tf, "Only two of 257 prints move more than ten points, so there is no "
         "intensity to exploit.", 13, INK, before=8, line=1.3)

tf = box(s, ML, 4.42, 4.9, 1.5)
para(tf, "CONTINUOUS DIFFERENCE-IN-DIFFERENCES", 9.5, GREY, bold=True, first=True, spc=150)
para(tf, "Not identified", 26, MUTED, bold=True, before=4)
para(tf, "The probability is the same for every country, so the date effects "
         "absorb it entirely.", 13, INK, before=8, line=1.3)

tf = box(s, 6.1, 2.15, 6.4, 0.35)
para(tf, "9 APRIL  —  THREE DAYS BEFORE THE VOTE", 10, GREY, bold=True,
     first=True, spc=150)
tf = box(s, 6.1, 2.45, 6.4, 0.75)
para(tf, "69%  vs  35%", 40, RED, bold=True, first=True)

picture(s, "fig6_implied.png", 6.1, 3.35, 6.4, 2.6)

tf = box(s, 6.1, 6.06, 6.4, 0.7)
para(tf, "They disagreed less about the level of risk than about when to price it.",
     14, NAVY, bold=True, first=True, line=1.25)
footer(s, 7)

# -------------------------------------------------------------------- slide 8
s = slide()
eyebrow(s, "Conclusion")
headline(s, "A real repricing, priced early")

kpi(s, ML, 2.45, 3.6, "−109 bp", "relative to neighbours, over the election window", RED, 38)
kpi(s, ML + 3.9, 2.45, 3.6, "65%", "of it came after the result, not before", RED, 38)
kpi(s, ML + 7.8, 2.45, 3.6, "first", "the prediction market moved before the bonds", NAVY, 38)

rule(s, ML, 3.95, CW, LIGHT, 0.025)

tf = box(s, ML, 4.2, CW, 0.9)
para(tf, "Hungarian sovereign risk fell about 109 basis points relative to its "
         "neighbours — 157 comparing endpoints — and two thirds of it came "
         "after the vote.", 17, INK, first=True, line=1.3)

band(s, ML, 5.45, CW, 0.95)
tf = box(s, ML + 0.4, 5.58, CW - 0.8, 0.7, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "CONDITIONAL ESTIMATE   One treated country, a pre-trend that cannot be "
         "removed, and a p-value floored at one in eight.", 14, NAVY, bold=True,
     first=True, line=1.2)
footer(s, 8)

# ---------------------------------------------------------------- validation
bad = []
for i, sl in enumerate(prs.slides, start=1):
    for sh in sl.shapes:
        right = (sh.left + sh.width) / 914400
        bottom = (sh.top + sh.height) / 914400
        if (sh.left < 0 or sh.top < 0 or right > W + 0.01 or bottom > H + 0.01):
            bad.append(f"slide {i}: {sh.shape_type} right={right:.2f} bottom={bottom:.2f}")
assert not bad, "shapes outside the slide:\n" + "\n".join(bad)

prs.save(DST)
print(f"wrote {DST}  ({len(prs.slides._sldIdLst)} slides, bounds checked)")
