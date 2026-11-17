# Response to comments

*Pricing Regime Change: Hungary's 2026 election and sovereign risk*
Jokūbas Narvydas and Levente Balogh · Empirical Finance · November 2026

This note lists what changed since the previous draft and why. It is organised by
category rather than by comment number, because several comments converged on the
same defect. Section 1 is the one that matters; the rest are corrections of fact,
figure or wording.

---

## 1. The comparison in Figure 6 was not comparing like with like

**The comment.** The bond-implied series and the prediction market were drawn on
one axis and read as if they were the same quantity. They were not.

**What was wrong.** The bond series is already a share of the eventual move:
`(S₀ − Sₜ)/(S₀ − S_T)`, which maps the 25 July spread to zero by construction.
Polymarket was plotted as a raw probability, and it opened at **0.385**. The
comparison therefore put a series reset to zero against one that had not been
reset, and credited the contract with roughly the size of its own starting point.
The "69 per cent against 35" reading was a level against a share.

**What changed.** Both series now enter as `share_t = (x_t − x₀)/(x_T − x₀)`,
with `x` the contract price or the spread. Both are zero on 25 July and one on
8 May. The formula is stated in Section 4, applied in Figure 6, and tabulated in
Table 8.

| Date | Spread (pp) | P | Contract share | Bond share |
|---|---:|---:|---:|---:|
| 25 Jul 2025 | 2.74 | 0.385 | 0.00 | 0.00 |
| 26 Feb 2026 | 2.35 | 0.625 | 0.39 | 0.25 |
| 31 Mar 2026 | 2.53 | 0.655 | 0.44 | 0.13 |
| 9 Apr 2026 | 2.18 | 0.685 | 0.49 | 0.35 |
| 12 Apr 2026 | 2.06 | 0.685 | 0.49 | 0.43 |
| 8 May 2026 | 1.16 | 1.000 | 1.00 | 1.00 |

**What survives.** The contract runs ahead of the spread on essentially every date
through the campaign, so the lead-lag reading holds.

**What does not.** "Twice as far." On 9 April the gap is thirteen points, a ratio
of 1.4 to 1; by the eve of the vote it is six points. That is a lead of weeks, not
a disagreement about what the election would do. The claim has been retired from
the abstract, the introduction, Sections 5.5, 7 and 8, and the deck.

**One month cuts against us and is now stated.** On 24 March the spread had given
back its entire early repricing (−6 per cent of its eventual move) in the global
selloff while the contract held near 42 per cent. That is a give-back, not a lead,
and Section 5.5 says so rather than smoothing it over.

**A second anchor removed.** The 13 November terminal reaches 1.438, outside the
unit interval. It is retained as a robustness note and not plotted.

---

## 2. Figure and table defects

| Item | Defect | Fix |
|---|---|---|
| Figure 1 | Twelve Hungarian market holidays left single-day gaps, so the headline series rendered as a dashed line. X-axis began in August while the title claimed July. Event labels touched the top spine. | Interpolated inside the window only, axis pinned to 25 July, headroom added before anchoring labels. |
| Figure 1 caption | Claimed every peer rose. Romania fell 21 bp. | "Hungary falls while the peer average rises." |
| Figure 2 | The caption described a chart that did not exist: it promised three controls over the event window in basis points and the figure drew two lines over 2022–2026 in percentage points. The blue line also duplicated Figure 4. | Rebuilt as three controls in basis points over the window: peer average (274 → 116), Bunds (441 → 275), Czechia (281 → 96). Figure 4 keeps the 2022–2026 path and the plateau argument. |
| Peer average | Code averaged whatever peers were present; the paper claimed a minimum of four. | Guard added. No reported value changes, because the only three-peer days are days Hungary is also missing. |
| Figure 6 | Undefined legend anchors, negative values unexplained, 9 April unmarked. | Normalisation formula in the subtitle, zero line drawn, 9 April annotated, anchors relabelled by date. Values below zero are explained as spreads widening past their 25 July level. |
| Figure 7 | The vertical line sat after February 2026, the reference month, so the caption "marks the election" was false. | Moved to the March–April boundary. |
| Table 8 | Titled "implied probability" while reporting shares. | Retitled, five columns, note defining the shares. |
| Prose | Display equations had real subscripts; running text kept literal underscores (`y_it`, `t_cut`). | Prose and inline maths now render true subscripts. |

---

## 3. Identification and inference

**Continuous difference-in-differences was described as unidentified. That was wrong.**
The deck claimed the date effects absorb the probability. They absorb `P_t`, which
is common to every country on a given day, but not `HU_i × P_t`, which varies
across countries within a date. The specification now runs in the pipeline:

| Specification | β | se | t | N |
|---|---:|---:|---:|---:|
| `HU × P × Post` | **−1.119** | 0.072 | −15.59 | 1,030 |
| `HU × P`, all periods | −2.353 | 0.267 | −8.82 | 1,030 |
| Binary DiD | −1.0897 | 0.096 | −11.32 | 3,200 |

Three basis points from the binary estimate. It is a **robustness result, not a
failure**, and has moved from "what fails" to Section 6. What the design gives up
is history: the contract begins 25 July 2025, so the panel is 1,030 country-days
against 3,200 and the nine flat quarters that make the binary design credible are
absent. That is the honest limitation, and it is now the stated one.

**The t-statistic is no longer offered as the precision measure.** `t = −11.3`
appears only alongside the fact that there is one treated country, where
conventional and Driscoll–Kraay standard errors over-reject. The binding statistic
is the randomisation-inference p-value of **0.125** on the eight-country panel,
which is the floor attainable with eight units. The deck now highlights that card.

**The event study baseline.** The reference month is February 2026, so the 2024–2025
leads sit above zero. The paper no longer says "leads oscillate, they do not trend"
as though that settled it: the leads are jointly non-zero (Wald 2,742 on 25 df,
mean +0.073, sd 0.163), which is why the pre-period trend is in the specification
rather than in a footnote.

**Treatment dates are stated.** `Post_t` and `t_cut` are both 13 April 2026, the
first trading day after the vote, under the equation on the identification slide
and in Section 4.

---

## 4. The four magnitudes, reconciled

Earlier drafts used four numbers for "the effect" without saying how they relate.
Each now has a defined quantity:

| Number | What it is | Where |
|---|---|---|
| −138 bp | Hungary's ten-year, 7.13 → 5.75, raw | §5.1, slide 2 |
| −157 bp | Hungary minus the peer average, endpoint to endpoint | §5.1, Table 2 |
| −109 bp | DiD coefficient over the election window | Table 9, slide 5 |
| −0.965 | The same coefficient on the 2025+ eight-country panel used for randomisation inference | §5.7.1 |

The gap between the last two is the sample and the trend treatment, not a
disagreement: on the five-country 2024+ panel the three trend specifications span
5 basis points (−1.039 none, −1.090 kinked, −1.091 linear).

Related wording changes: the conclusion no longer says "priced early", since 65 per
cent of the bond move came after the result; it says the contract moved first.
"Every neighbour's rose" became "One country repriced", with all seven peers named.
"Solved the pre-trend" was walked back to "a pre-trend that only a trend control
absorbs".

---

## 5. Deck

Rebuilt with a two-typeface hierarchy (Cambria for display and numerals, Calibri for
body), real hanging bullets, bordered cards, a running footer, and consistent panel
styling. The all-caps label run-ons are gone: labels and their claims are now separate
typographic elements in separate columns. Content, order and every number are
unchanged from what Section 1–4 describes. Eight slides: data, question, literature,
identification, robustness, what fails, conclusion.

---

## 6. Not changed, and why

**Contract volume and turnover.** The archived files carry prices and timestamps
only; no volume field exists, so no liquidity figure can be reported. The depth
evidence available is print frequency — two of 257 prints move more than ten points —
and that is what the paper and deck use. Reporting a turnover number would require
inventing one.

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

Figure 6 and Table 8 for Section 1. Figure 2 for the rebuilt controls. Section 6 for
the continuous design. Section 5.7 for the randomisation inference. Section 4 for the
share formula and the treatment dates.
