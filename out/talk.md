# Pricing Regime Change — 6-minute talk

Eight slides. Spoken text is about 675 words, which is **6:10 at 110 words per minute** — a slow,
deliberate pace — and about 5:30 at a normal one. Leave the rest of the ten minutes unused.

Rule for the whole talk: **say the number, then say what it means.** Never read a table. If you are
running late, drop slide 4 (literature) to two sentences; it is the only cuttable one.

---

## Slide 1 — Title (0:00–0:25)

**On slide**
- Pricing Regime Change: Hungary's 2026 Election and Sovereign Risk
- Did markets price the fall of a government before it fell?

**Say**
> On 12 April 2026 Viktor Orbán lost an election after sixteen years. Hungarian ten-year yields
> fell a long way — and they fell before he conceded. So the question is not whether they fell. It
> is whether the fall was about Hungarian politics, and when the market learned.

---

## Slide 2 — Data and the fact (0:25–1:10) — **Figure 1**

**On slide**
- Polymarket P(Orbán not PM), 257 daily prints; eight sovereign ten-year yields; July 2025 → May 2026
- HU 7.13 → 5.75 (**−138 bp**); six-peer average +19; Romania −21

**Say**
> Everything is public: Investing.com for yields, Polymarket's API for the probability, Yahoo
> Finance for controls.

> Between July 2025 and May 2026 the Hungarian ten-year fell 138 basis points. Every other market
> was flat or rose. Romania fell 21, less than a sixth as much. So this is not global duration. It is
> Hungary.

> The dark blue line is Hungary, the grey is the peer average. Look at the shape — it opens in two
> steps. That shape is the whole paper.

---

## Slide 3 — The question (1:10–1:55)

**On slide**
- **Question:** how much did the risk premium reprice, and when relative to the vote?
- Why Hungary: sixteen years of one government; EU funds frozen; a prediction market on the exact event

**Say**
> That is the fact. The question it raises has two halves. How much Hungarian sovereign risk
> did the market remove, and when — before the result or after?

> Hungary suits the question. Sixteen years of one government makes this regime risk, not a
> rotation. EU funds were frozen, so the result had a fiscal consequence. And there was a
> prediction market on the exact event — who becomes prime minister — printing daily for ten
> months. Normally we infer beliefs from spreads. Here I observe a probability.

---

## Slide 4 — The literature gap (1:55–2:45)

**On slide**
- Sign is contested: Block & Vaaler 2004 (falls into the vote), Balding 2011 (rises), Eichler 2014 (nothing)
- Panels average away the expectation
- **Gap:** never both instruments on one daily axis around a European election

**Say**
> The literature does not agree on the sign. Block and Vaaler find spreads fall into the vote.
> Balding, using daily CDS, finds the opposite. Eichler finds nothing once governance is
> controlled.

> They disagree because they are panels. A panel averages over events and throws away what the
> market expected beforehand.

> Prediction markets measure exactly that. So the gap is narrow but real: nobody has put a
> contract and a sovereign spread on the same daily axis around a European election. That is what
> lets me ask when, not just whether.

---

## Slide 5 — Identification (2:45–3:35) — **Table 9**

**On slide**
- Two-way fixed effects: country effects, date effects, country trend kinked at the treatment date
- **β = −1.09 pp** (t = −11.3), 2024–2026, N = 3,200
- No trend −1.04, linear −1.09: **five basis points apart**

**Say**
> Difference-in-differences against neighbouring markets. Country effects absorb level
> differences — why Hungary yields seven per cent and Germany two. Date effects absorb what all
> markets share on a day: global duration, US rates, VIX, risk appetite.

> What is left is the Hungarian, dated part of the move: 109 basis points.

> The number I would defend is the next one. No trend gives 104, a kinked trend 109, a linear
> trend 109. Five basis points apart. On a sample going back to 2022 those same three span
> sixty-three, which is why I start in 2024.

---

## Slide 6 — Does it survive? (3:35–4:50) — **Figures 7 and 8**

**On slide**
- Leads oscillate, they do not trend (mean +0.07)
- Fake election dates on a truncated panel: ≈ 0
- Every country treated in turn: Hungary −0.97, next +0.44
- **p = 0.125** — the floor with eight units

**Say**
> Four checks. One nearly kills the design.

> First, the pre-trend. Hungary's yield does drift relative to donors. But the leads oscillate;
> they do not trend into the treatment date. I report the joint rejection rather than hide it.

> Second, fake election dates, on a panel cut off before the real event. They come back at zero.
> On 2022 data the same test returns minus 1.1 at almost any date. That is why the sample starts
> in 2024 — a test, not a preference.

> Third, treat every country in turn. Hungary is minus 0.97; the next is plus 0.44. First of eight.

> Fourth, the ceiling. Eight units, one treated, so the smallest p-value is one eighth. That is
> what I get. My t-statistic counts days. Days are not the constraint. Countries are.

---

## Slide 7 — What fails, and what surprised me (4:50–5:40) — **Figure 6**

**On slide**
- Daily dose–response: β ≈ 0. Only two of 257 prints move more than 10 points
- 9 April, three days before the vote: **the contract had done 49% of its move, the spread 35%**

**Say**
> I wanted to regress daily spread changes on daily probability changes. It fails. Of 257 prints,
> two move more than ten points: the opening week, and one print after the result. There is no
> intensity to exploit, so the treatment is a date, not a price.

> The surprise is here. I can put both markets on one scale: how much of its own eventual
> repricing each had done. Three days before the vote the contract had done 49 per cent of its
> move, the spread 35. On that scale they agreed about where risk was going. They differed on how
> early to price it.

---

## Slide 8 — Conclusion (5:40–6:10)

**On slide**
- **−109 bp** relative to neighbours; two thirds of it after the result
- Prediction market led by weeks
- Conditional: one treated unit, p = 0.125

**Say**
> Hungarian sovereign risk fell about 109 basis points relative to its neighbours — 157 comparing
> endpoints — and two thirds of it came after the result. The prediction market moved first.

> The estimate is conditional. One treated country, a pre-trend that only a trend control
> absorbs, and a p-value floored at one in eight.

> Thank you.

---

# Q&A — prepared answers

Five minutes of questions. Answer in one sentence, then stop.

**"Your joint pre-trend test rejects. Doesn't that kill the DiD?"**
> It rejects that the leads are exactly zero, which at three hundred observations a month is a weak
> test. What would be fatal is a lead that *trends*, because a trend control cannot absorb a trend.
> There is none, and the proof is that all three trend treatments agree to five basis points. A
> reader who wants no trend assumption should read −1.04, not −1.09.

**"Why start in 2024? Isn't that just choosing your sample?"**
> The placebo dates say so. On 2022 data the design returns −1.1 at almost every fake election
> date, because of the 2022 disinflation convergence. On 2024 data the fake dates return zero. And
> the restriction costs nothing: the no-trends estimate *falls* from −1.46 to −1.04 when 2022 is
> dropped.

**"Your t-statistic is −11. Why then p = 0.125?"**
> Different things. Driscoll–Kraay counts time periods, and I have 3,200. The design has one
> treated unit, and with eight units there are eight assignments. Days are not the constraint;
> countries are.

**"What is the single biggest threat?"**
> That it was the central bank's easing cycle. The term structure argues against it: before the
> vote the ten-year fell 40 basis points while the five-year *rose* 13. Easing moves the short end.
> This moved the long end.

**"Isn't this just the EU funds story?"**
> Possibly, and I cannot separate them. EU funds and political risk both predict a long-end
> compression and both arrive in the same weeks, so they are observationally equivalent here. No
> control group fixes that with one treated unit.

**"Is Polymarket reliable? It's banned in Hungary."**
> No. It is thin, manipulable, and its users are self-selected foreign observers. I use it as a
> proxy for a probability, never as truth. The lead–lag result needs the two series measured
> consistently, not for Polymarket to be right.

**"Balding already did daily CDS around elections. What is new?"**
> His sign is the opposite of mine, which is why the paper exists. But he has no measure of what
> the market expected, so he cannot separate anticipation from disappointment. I have the contract
> price, so I can. He has thirteen countries over three years; I have one over ten months. That is
> the reverse trade — less external validity, but the timing question is only answerable the second
> way.

**"Why not synthetic control?"**
> Six donors is too few for a credible counterfactual, and Hungary's yield sits outside the convex
> hull of its neighbours for most of the pre-period. The DiD with country trends is the honest
> compromise.

---

# Numbers card — six, and no more

| | |
|---|---|
| DiD, kinked trend | **−109 bp** |
| No trend / linear trend | −104 / −109 bp |
| Hungary's own fall | −138 bp |
| After the result, not before | 65% |
| Randomisation inference | p = 0.125 (floor) |
| 9 April: contract vs bonds | 49% of its move vs 35% |
