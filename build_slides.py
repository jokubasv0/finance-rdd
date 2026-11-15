"""Build the presentation deck from the paper's numbers and figures.

Eight slides, 16:9, matching out/talk.md slide for slide. Figures are read
from out/, so the deck cannot drift from the paper. Every shape is bounds
checked against the slide before saving.

Type: Cambria for display (Caladea here, identical metrics), Calibri for text
(Carlito here, identical metrics). Both are present in every Office install,
so the deck travels without carrying font files.
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

# ---------------------------------------------------------------- palette
INK = RGBColor(0x14, 0x1B, 0x26)        # body text, near-black with a blue cast
NAVY = RGBColor(0x14, 0x38, 0x5C)       # headlines and structure
NAVY_DEEP = RGBColor(0x0E, 0x24, 0x3B)  # full-bleed cover, emphasis panels
RED = RGBColor(0xA5, 0x14, 0x2E)        # the single accent, used sparingly
GREY = RGBColor(0x57, 0x61, 0x70)
MUTED = RGBColor(0x93, 0x9C, 0xAA)
BORDER = RGBColor(0xDC, 0xE2, 0xEA)
LIGHT = RGBColor(0xEE, 0xF2, 0xF7)
TINT = RGBColor(0xFB, 0xF3, 0xF4)       # the one warning tint
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ON_DARK = RGBColor(0xC9, 0xD6, 0xE4)
ON_NAVY_MUTED = RGBColor(0x8F, 0xA8, 0xC2)

DISPLAY = "Cambria"     # headlines and numerals
BODY = "Calibri"        # everything else

W, H = 13.333, 7.5
ML = 0.9
CW = W - 2 * ML
BASE = 6.94             # footer hairline

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
            r = p.add_run(); r.text = gap
            r.font.name = BODY; r.font.size = Pt(size)
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
    """Fill a shape, remove the theme style (which adds a drop shadow), and
    optionally give it a hairline border."""
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
    """A flat panel with an optional accent bar down the left edge."""
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
    if h > max_h:                      # height limited
        h = max_h
        w = h * aspect
    s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
    if cap:
        tf = box(s, x, y + h + 0.12, w, 0.5)
        para(tf, cap, cap_size, GREY, italic=True, first=True, line=1.3)
    return y + h


def footer(s, n):
    hline(s, ML, BASE, CW, BORDER, 0.008)
    tf = box(s, ML, BASE + 0.1, 8.0, 0.26)
    para(tf, "PRICING REGIME CHANGE   ·   NARVYDAS & BALOGH", 8, MUTED,
         bold=True, first=True, spc=110)
    tf2 = box(s, W - ML - 0.9, BASE + 0.08, 0.9, 0.3)
    para(tf2, f"{n} / 8", 8.5, GREY, bold=True, first=True, align=PP_ALIGN.RIGHT)


# -------------------------------------------------------------------- slide 1
s = slide(NAVY_DEEP)


tf = box(s, ML + 0.05, 1.22, 9.0, 0.3)
para(tf, "EMPIRICAL FINANCE   ·   FINAL PRESENTATION", 10.5, ON_NAVY_MUTED,
     bold=True, first=True, spc=220)

tf = box(s, ML, 1.78, 9.6, 1.9)
para(tf, "Pricing Regime Change", 54, WHITE, bold=True, first=True, line=1.02,
     font=DISPLAY)

tf = box(s, ML, 3.42, 9.6, 0.6)
para(tf, "Hungary's 2026 election and sovereign risk", 25, ON_DARK, first=True,
     line=1.15)

rect(s, ML, 4.32, 2.1, 0.045, RED)

tf = box(s, ML, 4.72, 8.9, 1.0)
para(tf, "Did markets price the fall of a government\nbefore it fell?",
     21, RGBColor(0xF3, 0xC3, 0xC8), italic=True, first=True, line=1.3)

hline(s, ML, 6.02, CW, RGBColor(0x2A, 0x44, 0x5E), 0.008)

tf = box(s, ML, 6.2, 8.0, 0.75)
para(tf, "Jokūbas Narvydas   ·   Levente Balogh", 14, WHITE, bold=True,
     first=True)
para(tf, "November 2026", 11.5, ON_NAVY_MUTED, before=5)

# -------------------------------------------------------------------- slide 2
s = slide()
eyebrow(s, "Data and the fact")
headline(s, "One country repriced.\nThe others did not.", 30, w=5.0)

kpi(s, ML, 2.02, 4.45, "−138 bp", "Hungary's ten-year yield, 7.13% → 5.75%", RED, 36)
kpi(s, ML, 3.10, 4.45, "+19 bp", "Average of the six peers — Germany is shown "
                                 "separately", NAVY, 36)
kpi(s, ML, 4.30, 4.45, "−21 bp", "Romania — the only other faller", GREY, 36)

picture(s, "fig1_levels.png", 5.92, 1.52, 6.55, 3.45,
        cap="Hungary in dark blue, the peer average in grey. The fall opens in "
            "two steps — before the vote, and after it.")

tf = box(s, ML, 5.68, 5.0, 0.4)
para(tf, "Hungary and seven peers: Czechia, Poland, Romania, Germany, Austria, "
         "Slovenia, Croatia.", 9.5, MUTED, first=True, line=1.3)

panel(s, ML, 6.22, CW, 0.56, fill=LIGHT, bar=True, bar_colour=RED)
tf = box(s, ML + 0.28, 6.22, CW - 0.5, 0.56, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "That shape is the whole paper: not that yields fell, but where and when.",
     15, NAVY, bold=True, first=True)
footer(s, 2)

# -------------------------------------------------------------------- slide 3
s = slide()
eyebrow(s, "The question")
headline(s, "Two questions: how much, and when")

for i, (num, label, text) in enumerate([
        ("01", "How much", "Did the risk premium really reprice around the vote?"),
        ("02", "When", "Before the result — or only after it?")]):
    x = ML + i * 5.98
    card(s, x, 2.12, 5.55, 1.44, f"{num}   {label}", text, accent=RED,
         body_size=19, label_size=9.5)

tf = box(s, ML, 3.95, 7.0, 0.3)
para(tf, "WHY HUNGARY", 9.5, GREY, bold=True, first=True, spc=180)

tf = box(s, ML, 4.32, 8.4, 1.4)
bullets(tf, ["Sixteen years of one government — regime risk, not a routine "
             "rotation",
             "EU funds frozen — the result carried a fiscal consequence",
             "A prediction market on the exact event, printing daily for ten months"],
        size=14.5, before=8)

panel(s, ML, 6.14, CW, 0.56, fill=LIGHT, bar=True, bar_colour=RED)
tf = box(s, ML + 0.28, 6.14, CW - 0.5, 0.56, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "Normally we infer beliefs from spreads. Here we observe a probability.",
     13.5, RED, italic=True, first=True)
footer(s, 3)

# -------------------------------------------------------------------- slide 4
s = slide()
eyebrow(s, "The literature")
headline(s, "The sign is contested, because panels\nthrow away what markets "
            "expected", 28, y=0.78)

y = 2.18
for name, claim in [("Block & Vaaler, 2004", "Sovereign spreads fall into the vote"),
                    ("Balding, 2011", "Daily CDS: they rise"),
                    ("Eichler, 2014", "Nothing, once governance is controlled")]:
    hline(s, ML, y, CW, BORDER)
    tf = box(s, ML, y + 0.16, 3.9, 0.4)
    para(tf, name, 15, NAVY, bold=True, first=True)
    tf = box(s, ML + 3.9, y + 0.16, 7.5, 0.4)
    para(tf, claim, 15, INK, first=True)
    y += 0.72
hline(s, ML, y, CW, BORDER)

tf = box(s, ML, 4.5, 10.2, 0.7)
para(tf, "A panel averages over events. The expectation that made each event "
         "matter is the one thing it discards.", 14.5, GREY, italic=True,
     first=True, line=1.3)

panel(s, ML, 5.3, CW, 1.26, fill=NAVY_DEEP)
for i, (label, text, lab_col, txt_col) in enumerate([
        ("The gap",
         "Nobody has put a contract and a sovereign spread on the same daily "
         "axis around a European election.", RGBColor(0xF3, 0xC3, 0xC8), WHITE),
        ("Our contribution",
         "That joint daily measurement, which is what lets the timing question "
         "be asked at all.", ON_NAVY_MUTED, ON_DARK)]):
    yy = 5.44 + i * 0.58
    tf = box(s, ML + 0.42, yy, 1.95, 0.4)
    para(tf, label.upper(), 8.5, lab_col, bold=True, first=True, spc=150)
    tf = box(s, ML + 2.45, yy - 0.03, 8.75, 0.62)
    para(tf, text, 13.5, txt_col, first=True, line=1.28)
footer(s, 4)

# -------------------------------------------------------------------- slide 5
s = slide()
eyebrow(s, "Identification")
headline(s, "Difference-in-differences against\nneighbouring markets", 30)

panel(s, ML, 2.16, CW, 0.62, fill=LIGHT)
tf = box(s, ML + 0.3, 2.16, CW - 0.6, 0.62, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "yᵢₜ = αᵢ + λₜ + β(HUᵢ × Postₜ) + γᵢ · min(t, t_cut) + εᵢₜ", 19, NAVY,
     first=True, font=DISPLAY)

tf = box(s, ML, 2.94, 10.9, 0.8)
para(tf, "country effects   ·   date effects   ·   a country trend fitted before "
         "the vote and held flat after it", 11, GREY, first=True, line=1.3)
para(tf, "Postₜ switches on 13 April 2026, the first trading day after the vote; "
         "t_cut is the same date.", 11, GREY, before=3, line=1.3)

tiles = [("−1.04", "no trend", NAVY, False),
         ("−1.09", "kinked trend — the headline", RED, True),
         ("−1.09", "linear trend", NAVY, False)]
for i, (num, lab, col, hot) in enumerate(tiles):
    x = ML + i * 3.94
    panel(s, x, 3.84, 3.62, 0.94, fill=(TINT if hot else WHITE),
          border=(RGBColor(0xE6, 0xC0, 0xC7) if hot else BORDER), bar=True,
          bar_colour=(RED if hot else NAVY), bar_w=0.045)
    tf = box(s, x + 0.28, 3.95, 3.1, 0.5)
    para(tf, num, 30, col, bold=True, first=True, line=1.0, font=DISPLAY)
    tf = box(s, x + 0.28, 4.5, 3.1, 0.26)
    para(tf, lab, 10.5, GREY, first=True)

tf = box(s, ML, 5.06, 8.4, 0.4)
para(tf, "Five basis points apart.", 18, INK, bold=True, first=True, font=DISPLAY)

tf = box(s, ML, 5.62, 10.9, 1.1)
para(tf, "On a sample reaching back to 2022 the same three specifications span "
         "sixty-three basis points, because the 2022 disinflation is "
         "indistinguishable from an election effect. That is why the sample "
         "starts in 2024 — a test, not a preference.", 11.5, GREY, first=True,
     line=1.38)

tf = box(s, ML, 6.5, CW, 0.3)
para(tf, "Driscoll–Kraay t = −11.3   ·   N = 3,200   ·   one treated country, so t "
         "is not the binding statistic", 9, MUTED, first=True,
     align=PP_ALIGN.RIGHT)
footer(s, 5)

# -------------------------------------------------------------------- slide 6
s = slide()
eyebrow(s, "Robustness")
headline(s, "Four checks. One nearly\nkills the design.", 29, w=5.3)

checks = [
    ("01", "Pre-trend", "Leads oscillate, mean +0.07, no drift — but jointly "
                        "non-zero, so the trend carries weight.", False),
    ("02", "Fake election dates", "On a panel cut before the event: ≈ 0.", False),
    ("03", "Every country in turn", "Hungary −0.97. The next is +0.44.", False),
    ("04", "The ceiling", "p = 0.125 — the floor with eight units.", True)]
y = 2.12
for num, name, claim, hot in checks:
    card(s, ML, y, 5.25, 0.96, f"{num}   {name}", claim,
         accent=(RED if hot else NAVY), tint=(TINT if hot else None),
         border=(RGBColor(0xE6, 0xC0, 0xC7) if hot else BORDER),
         body_size=12, label_size=8.5)
    y += 1.1

picture(s, "fig7_event_study.png", 6.45, 1.78, 6.0, 2.8,
        cap="Pre-treatment leads oscillate around zero; the break lands after "
            "the vote, not before it.")

card(s, 6.45, 5.32, 5.95, 1.16, "Alternative estimator",
     "Intensity (Hungary × P): −1.12 — three basis points from the binary "
     "estimate.", accent=NAVY, body_size=12, label_size=8.5)
footer(s, 6)

# -------------------------------------------------------------------- slide 7
s = slide()
eyebrow(s, "What fails")
headline(s, "What fails, and what surprised us")

panel(s, ML, 2.12, 4.8, 1.82, fill=WHITE, border=BORDER, bar=True,
      bar_colour=MUTED, bar_w=0.05)
tf = box(s, ML + 0.3, 2.27, 4.25, 0.24)
para(tf, "DAILY CHANGES", 8.5, MUTED, bold=True, first=True, spc=140)
tf = box(s, ML + 0.3, 2.49, 4.25, 0.48)
para(tf, "β ≈ 0", 28, RGBColor(0x8A, 0x93, 0xA1), bold=True, first=True,
     line=1.0, font=DISPLAY)
tf = box(s, ML + 0.3, 3.02, 4.25, 0.8)
para(tf, "Two of 257 prints move more than ten points, so a regression on daily "
         "changes is mostly regression on staleness.", 11.5, INK, first=True,
     line=1.28)

panel(s, ML, 4.12, 4.8, 1.62, fill=WHITE, border=BORDER, bar=True,
      bar_colour=NAVY, bar_w=0.05)
tf = box(s, ML + 0.3, 4.28, 4.25, 0.24)
para(tf, "NOT MONETARY POLICY", 8.5, NAVY, bold=True, first=True, spc=140)
tf = box(s, ML + 0.3, 4.53, 4.25, 0.3)
para_runs(tf, [("10Y  −40 bp", NAVY, True), ("5Y  +13 bp", NAVY, True),
               ("HUF  +10%", NAVY, True)], 12.5, first=True, gap="     ")
tf = box(s, ML + 0.3, 4.9, 4.25, 0.7)
para(tf, "The long end fell while the front end rose, and the forint "
         "appreciated. Long-end risk, not rate cuts.", 11.5, INK, first=True,
     line=1.28)

tf = box(s, 5.98, 2.02, 6.3, 0.3)
para(tf, "9 APRIL   ·   THREE DAYS BEFORE THE VOTE", 9.5, RED, bold=True,
     first=True, spc=160)
tf = box(s, 5.98, 2.3, 6.3, 0.8)
para(tf, "69%  vs  35%", 42, RED, bold=True, first=True, line=1.0, font=DISPLAY)

picture(s, "fig6_implied.png", 5.98, 3.12, 6.35, 2.78)

tf = box(s, 5.98, 6.14, 6.35, 0.5)
para(tf, "They agreed on the level of risk, not on when to price it.", 14, NAVY,
     bold=True, first=True)
footer(s, 7)

# -------------------------------------------------------------------- slide 8
s = slide()
eyebrow(s, "Conclusion")
headline(s, "A real repricing. The contract saw it first.", 31, y=0.8)

for i, (num, lab, col) in enumerate([
        ("−109 bp", "relative to neighbours, over the election window", RED),
        ("65%", "of it came after the result, not before", RED),
        ("first", "the prediction market moved before the bonds", NAVY)]):
    kpi(s, ML + i * 3.9, 2.14, 3.6, num, lab, col, numsize=42, labsize=10.5)

tf = box(s, ML, 4.02, CW, 0.9)
para(tf, "Hungarian sovereign risk fell about 109 basis points relative to its "
         "neighbours — 157 comparing endpoints — and two thirds of it came after "
         "the vote.", 16.5, INK, first=True, line=1.32)

panel(s, ML, 5.32, CW, 1.0, fill=NAVY_DEEP)
tf = box(s, ML + 0.42, 5.32, 2.0, 1.0, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "CONDITIONAL ESTIMATE", 8.5, RGBColor(0xF3, 0xC3, 0xC8), bold=True,
     first=True, spc=150)
tf = box(s, ML + 2.4, 5.32, 8.6, 1.0, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "One treated country, a pre-trend only a trend control absorbs, and a "
         "p-value floored at one in eight.", 13.5, WHITE, first=True, line=1.3)
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
