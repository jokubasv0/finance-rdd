# Response to comments

*Pricing Regime Change: Hungary's 2026 election and sovereign risk*
Jokūbas Narvydas and Levente Balogh · Empirical Finance · November 2026

This note lists what changed since the previous draft and why. It is organised by
category rather than by comment number, because several comments converged on the
same defect. Section 1 is the one that matters; the rest are corrections of fact,
figure or wording.

Two changes came after the comments and are ours rather than anyone's request. The
estimation window now starts on 4 August 2025, dropping the first week of the
prediction-market contract; and every reported magnitude has been recomputed on that
window. Section 0 records both, because they move numbers that appear throughout the
paper, the deck and the speech.

---

## 0. The window, and what it does to the second result

**Why the first week goes.** The contract printed its first price on 25 July 2025 at
0.615 (so P(Orbán leaves) = 0.385) and repriced to 0.645 by 1 August — 26 points
across seven prints, on almost no volume. Over the same days the Hungarian ten-year
*yield rose*, 7.13 to 7.24 per cent. That week is a price being found, not news, and
including it loads the entire subsequent comparison. We tested a second week of
exclusion on 11 August 2025 and rejected it: the yield that day is 7.00, mid-fall, so
the start date would be arbitrary rather than anchored to anything, and the
comparison's gap shrinks from 21 points to 5.

**Why 4 August and not 1 August.** Hungarian yields spiked to 7.24 on 1 August and
reversed to 7.11 on 4 August. Starting on 1 August would date the window to a
two-day local spike and inflate every reported fall by about 13 basis points for a
reason unrelated to the election. The window therefore begins on the first trading
day after that reversal.

**What moves.** Window 4 August 2025 → 8 May 2026: 217 calendar days, 200 trading
days, 188 Hungarian observations. Hungary's ten-year **7.11 → 5.75 (−136 bp)**;
the peer average **+24**; the spread over peers **2.76 → 1.16 (−160 bp)**. The
decomposition is 59 bp before the vote (37 per cent) and 102 after it (63 per cent).
The DiD coefficient and all robustness checks are unchanged in size and sign.

**What reverses.** See Section 1. The bond market now leads the contract, not the
other way round.

---

## 1. Figure 6 compared a share with a level, and the ordering was the wrong way

**The comment.** The bond-implied series and the prediction market were drawn on one
axis and read as if they were the same quantity. They were not.

**What was wrong.** The bond series is already a share of the eventual move:
`(S₀ − Sₜ)/(S₀ − S_T)`, which maps the initial spread to zero by construction.
Polymarket was plotted as a raw probability, which opened at 0.385. The comparison
therefore put a series reset to zero against one that had not been reset, and
credited the contract with roughly the size of its own starting point. The
"69 per cent against 35" reading was a level against a share.

**What changed.** Both series enter as `share_t = (x_t − x₀)/(x_T − x₀)`, with `x`
the contract price or the spread. Both are zero on 4 August 2025 and one on
8 May 2026. The formula is stated in Section 4, applied in Figure 6, and tabulated
in Table 8.

| Date | Spread (pp) | P | Contract share | Bond share |
|---|---:|---:|---:|---:|
| 4 Aug 2025 | 2.76 | 0.625 | 0.00 | 0.00 |
| 26 Feb 2026 | 2.35 | 0.625 | 0.00 | 0.26 |
| 31 Mar 2026 | 2.53 | 0.655 | 0.08 | 0.15 |
| 9 Apr 2026 | 2.18 | 0.685 | 0.16 | 0.37 |
| 12 Apr 2026 | 2.06 | 0.685 | 0.16 | 0.44 |
| 8 May 2026 | 1.16 | 1.000 | 1.00 | 1.00 |

**What the corrected comparison shows, which we did not expect.** On a like-for-like
scale the spread leads and the contract lags. Three days before the vote the spread
had completed 37 per cent of its eventual move and the contract 16, a gap of
twenty-one points *in the spread's favour*; by the eve it is 44 against 16, a gap of
twenty-eight. The contract sat between 0.625 and 0.685 for eight months and did not
move decisively until the count.

**What we claim, and what we no longer do.** The previous draft claimed the
prediction market moved first. In this window it did not: the spread was ahead at
every recorded date before the vote. But moving the base date back ten days reverses
the ordering, so the paper now claims the divergence in timing and expressly not a
ranking. The abstract, introduction, Sections 5.5, 7 and 8, the deck and the speech
all say the two markets were on different clocks and decline to name a leader.

**The base-date sensitivity, tabulated.** Section 6 carries this as Table 14 rather
than as a sentence, because the sentence could be read as a hedge and the table
cannot:

| Base date | Spread (pp) | P | Spread share | Contract share | Gap |
|---|---:|---:|---:|---:|---:|
| 25 Jul 2025 | 2.74 | 0.385 | 0.354 | 0.488 | +13 |
| 4 Aug 2025 | 2.76 | 0.625 | 0.366 | 0.160 | −21 |
| 11 Aug 2025 | 2.64 | 0.575 | 0.311 | 0.259 | −5 |
| 1 Sep 2025 | 2.75 | 0.605 | 0.358 | 0.203 | −15 |
| 1 Oct 2025 | 2.49 | 0.600 | 0.232 | 0.213 | −2 |
| 3 Nov 2025 | 2.58 | 0.565 | 0.285 | 0.276 | −1 |

The spread's share moves between 23 and 37 per cent across all six anchors; the
contract's moves between 16 and 49. One series is stable and the other is not, because
almost all of the contract's early movement happened in its first week. A comparison
whose sign depends on where the clock starts does not identify leadership, and the
paper does not use it to.

**One month cuts against the reversal and is now stated.** On 24 March the spread had
given back its early repricing (−4 per cent of its eventual move) in the global
selloff while the contract held near 5 per cent. That is not evidence either way.

**A second anchor removed.** The 13 November terminal pushes the bond share outside
the unit interval, because the spread keeps narrowing past 8 May. It is retained as a
robustness note and not plotted.

---

## 2. Figure and table defects

| Item | Defect | Fix |
|---|---|---|
| Figure 1 | Twelve Hungarian market holidays left single-day gaps, so the headline series rendered as a dashed line. X-axis began in August while the title claimed July. Event labels touched the top spine. | Interpolated inside the window only, axis pinned to the window start, headroom added before anchoring labels. |
| Figure 1 caption | Claimed every peer rose. Romania fell 26 bp. | "Hungary falls while the peer average rises." |
| Figure 2 | The caption described a chart that did not exist: it promised three controls over the event window in basis points and the figure drew two lines over 2022–2026 in percentage points. The blue line also duplicated Figure 4. | Rebuilt as three controls in basis points over the window: peer average (276 → 116), Bunds (448 → 275), Czechia (283 → 96). Figure 4 keeps the 2022–2026 path and the plateau argument. |
| Peer average | Code averaged whatever peers were present; the paper claimed a minimum of four. | Guard added. No reported value changes, because the only three-peer days are days Hungary is also missing. |
| Figure 3 | Caption dated the series January 2022 to November 2026 while it plots only the event window. | Caption re-dated to the window. |
| Figure 5 | X-axis labels ran together into one unreadable string. | Month locator and formatter added. |
| Figure 6 | Undefined legend anchors, negative values unexplained, 9 April unmarked. | Normalisation formula in the subtitle, zero line drawn, 9 April annotated, anchors relabelled by date. Values below zero are explained as a series having moved against its eventual direction. |
| Figure 7 | The vertical line sat after February 2026, the reference month, so the caption "marks the election" was false. | Moved to the March–April boundary. |
| Table 8 | Titled "implied probability" while reporting shares. | Retitled, five columns, re-anchored to 4 August, note defining the shares. |
| Prose | Display equations had real subscripts; running text kept literal underscores (`y_it`, `t_cut`). | Prose and inline maths now render true subscripts. |
| Table layout | Numeric columns were fixed narrow, so two-word headers wrapped to three lines and tables jumped whole pages, leaving one page 40 per cent blank. | Column widths fitted per column; cell padding tightened; no blank half-pages. |

---

## 3. Identification and inference

**Continuous difference-in-differences was described as unidentified. That was wrong.**
The deck claimed the date effects absorb the probability. They absorb `P_t`, which
is common to every country on a given day, but not `HU_i × P_t`, which varies
across countries within a date. The specification now runs in the pipeline:

| Specification | β | se | t | N |
|---|---:|---:|---:|---:|
| `HU × P × Post` | **−1.128** | 0.073 | −15.55 | 1,000 |
| `HU × P`, all periods | −2.466 | 0.346 | −10.30 | 1,000 |
| Binary DiD | −1.0897 | 0.096 | −11.32 | 3,200 |

Four basis points from the binary estimate. It is a **robustness result, not a
failure**, and has moved from "what fails" to Section 6. What the design gives up is
history: the contract is usable from 4 August 2025, so the panel is 1,000
country-days against 3,200, and the nine flat quarters that make the binary design
credible are absent. That is the honest limitation, and it is now the stated one.

**The t-statistic is no longer offered as the precision measure.** `t = −11.3`
appears only alongside the fact that there is one treated country, where conventional
and Driscoll–Kraay standard errors over-reject. The binding statistic is the
randomisation-inference p-value of **0.125** on the eight-country panel, which is the
floor attainable with eight units. The deck highlights that card.

**The event study baseline.** The reference month is February 2026, so the 2024–2025
leads sit above zero. The paper no longer says "leads oscillate, they do not trend" as
though that settled it: the leads are jointly non-zero (Wald 2,742 on 25 df, mean
+0.073, sd 0.163), which is why the pre-period trend is in the specification rather
than in a footnote.

**Treatment dates are stated.** `Post_t` and `t_cut` are both 13 April 2026, the
first trading day after the vote, under the equation on the identification slide and
in Section 4.

---

## 4. The four magnitudes, reconciled

Earlier drafts used four numbers for "the effect" without saying how they relate.
Each now has a defined quantity:

| Number | What it is | Where |
|---|---|---|
| −136 bp | Hungary's ten-year, 7.11 → 5.75, raw | §5.1, slide 2 |
| −160 bp | Hungary minus the peer average, endpoint to endpoint | §5.1, Table 2 |
| −109 bp | DiD coefficient over the election window | Table 9, slide 5 |
| −0.965 | The same coefficient on the 2025+ eight-country panel used for randomisation inference | §5.7.1 |

The gap between the last two is the sample and the trend treatment, not a
disagreement: on the five-country 2024+ panel the three trend specifications span
5 basis points (−1.039 none, −1.090 kinked, −1.091 linear).

Related wording changes: "every neighbour's rose" became "One country repriced", with
all seven peers named; "solved the pre-trend" was walked back to "a pre-trend that
only a trend control absorbs"; and the timing claim was reversed (Section 1).

---

## 5. Deck

Rebuilt with a two-typeface hierarchy (Cambria for display and numerals, Calibri for
body), real hanging bullets, bordered cards, a running footer, and consistent panel
styling. The all-caps label run-ons are gone: labels and their claims are now separate
typographic elements in separate columns. Eight slides: data, question, literature,
identification, robustness, what fails, conclusion. Every number on them is the
recomputed 4 August figure.

---

## 6. Not changed, and why

**Contract volume and turnover.** The archived files carry prices and timestamps
only; no volume field exists, so no liquidity figure can be reported. The depth
evidence available is print frequency — two of 257 prints move more than ten points —
and that is what the paper and deck use. Reporting a turnover number would require
inventing one. The opening week is excluded precisely because it is the one stretch
where that thinness plainly distorts the series.

**The robustness section stays.** The brief asks for robustness checks including what
kills the results; that is what Section 6 is.

**The 2022 sample stays excluded.** The exclusion is justified by a placebo-date
test on a panel truncated at 10 April 2026, not by preference. On 2022 the three trend
treatments differ by 63 basis points; on 2024+ they differ by 5.

**A random-window placebo was withdrawn.** It is invalid for a trending series and
appeared in an earlier draft. Removing it was our correction, not a response to a
comment.

---

## 7. Where to look

Figure 6 and Table 8 for Sections 0 and 1. Figure 2 for the rebuilt controls.
Section 6 for the continuous design. Section 5.7 for the randomisation inference.
Section 4 for the share formula and the treatment dates.
