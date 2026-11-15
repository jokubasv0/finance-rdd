# Pricing Regime Change — 10-minute talk

Ten slides, 10 min 00 s with 30 s buffer. Cue times are cumulative.

Rule for the whole talk: **say the number, then say what it means.** Never read a table.

---

## Slide 1 — Title (0:00–0:30)

**On slide**
- Pricing Regime Change: Hungary's 2026 Election and Sovereign Risk
- One question: *did markets price the fall of a government before it fell?*
- Daily data, July 2025 – November 2026

**Say**
> On 12 April 2026 Viktor Orbán lost an election. Hungary's ten-year yield had already fallen by the time he conceded. The question is not whether yields fell — they did — but whether the movement was about Hungarian politics, and when the market learned.

---

## Slide 2 — Why this case (0:30–1:25)

**On slide**
- 16 years of one government, supermajority result
- EU cohesion funds frozen
- A liquid prediction market on the exact event: $101 million

**Say**
> Hungary is unusually good for this question. Sixteen years of one government means the election is genuine regime risk, not a rotation. EU funds were frozen, so the result had a direct fiscal consequence.

> And uniquely there was a prediction market on the exact event — who becomes prime minister — with 101 million dollars of volume. Normally we infer beliefs from prices. Here we observe a probability directly, daily.

---

## Slide 3 — Data (1:25–2:15)

**On slide**
- Polymarket: P(Orbán not PM), daily, 257 prints (weekends kept)
- Ten-year yields: HU, CZ, PL, RO, SI, HR, AT, DE
- Also 5Y, EUR/HUF, US 10Y, VIX, Brent
- Window 25 Jul 2025 → 8 May 2026; panel 2022–2026

**Say**
> Everything is free and public: Investing.com for yields, Polymarket's own API for the probability, Yahoo Finance for global controls.

> One early correction. My first draft compared Hungary only to Czechia. Czechia turns out to be the most generous possible control — Czech yields rose 47 basis points while Hungary's fell 138. So the design uses seven other countries, and I report Czechia only as an upper bound.

---

## Slide 4 — The fact (2:15–3:20) — **Figure 1**

**On slide**
- HU 10Y: 7.13 → 5.75 (**−138 bp**)
- Hungary is the **only one of eight** whose yield fell
- Peer average rose 19 bp; Czechia +47; Bund +29

**Say**
> Between July 2025 and May 2026 the Hungarian ten-year fell 138 basis points. Every peer went the other way or stayed flat.

> The red line is Hungary, the grey is the peer average. The divergence is not gradual — it opens in two steps, and that shape is the whole paper.

---

## Slide 5 — Identification (3:20–4:45) — **Table 9**

**On slide**
- Two-way FE DiD: country effects + date effects + country trend
- $y_{it} = α_i + λ_t + β(HU_i × Post_t) + γ_i·min(t,t_{cut}) + ε_{it}$
- **β = −1.09 pp** (DK t = −11.3), 2024–2026, N = 3,200
- No trend −1.04, linear trend −1.09: **five basis points apart**

**Say**
> The identification is difference-in-differences against neighbouring markets. Country fixed effects absorb level differences — the reason Hungary yields seven per cent and Germany two. Date fixed effects absorb everything common to all markets on a given day: global duration, US rates, VIX, regional risk appetite.

> What is left is the Hungarian, dated, part of the move. On a 2024 sample that is 109 basis points.

> The number I care about is not that one, it is the next one: −1.04 with no trend, −1.09 with a kinked trend, −1.09 with a linear trend. Five basis points apart. On a sample going back to 2022 those same three specifications span sixty-three basis points, which is why I start in 2024 — and I will show you the test that justifies it rather than just asserting it.

---

## Slide 6 — The diagnostic that nearly kills it (4:45–6:10) — **Figure 7**

**On slide**
- Monthly leads and lags relative to February 2026
- Leads **oscillate**, they do not trend: mean +0.07, range −0.27 to +0.37
- Joint test rejects zero (Wald 2,742, 25 df) — because 0.1 pp is precise at 300 obs/month
- Break is **after** the vote: Apr −0.63, May −1.12
- Placebo dates on a truncated panel: all ≈ 0

**Say**
> This is the slide I would rather not show, and it is the most important one.

> The leads bounce around zero. They do not trend into the treatment date. But a joint test rejects that they are all zero, and I report that rather than claiming parallel trends holds.

> Why does the rejection not kill the design? Because at three hundred observations a month, a coefficient of one tenth of a point is precisely estimated. What would kill it is a lead that trends up or down as the election approaches, since that is what a trend control cannot absorb. There is none, and the corroboration is that the trend treatment changes the answer by five basis points.

> The other check is the one that decided the sample. I re-run the whole design at fake election dates, on a panel cut off before the real event. On 2024 data every fake date returns essentially zero. On a sample starting in 2022 the no-trends version returns minus 1.1 at almost any date — because of the 2022 energy-crisis convergence. That is why the paper starts in 2024, and it is a test, not a preference.

> Look where the break sits: April minus 0.6, May minus 1.1. Two thirds of the movement is after the vote, not before.

---

## Slide 7 — Placebos and the ceiling (6:10–7:15) — **Figure 8**

**On slide**
- Each country treated in turn: HU −0.97, next Croatia +0.00, rest up to +0.44
- Randomisation inference: **p = 0.125**
- That is the floor: 1/8 with eight units

**Say**
> Run the identical specification treating each country as if it were the event. Hungary is the only negative of any size, and it is more than twice the largest positive.

> Then the honest constraint. With eight units and one treated there are eight possible assignments, so the smallest p-value I can ever report is one eighth. That is what I get. My t-statistic of minus eleven is arithmetic, not evidence — it counts days, and days are not the binding constraint. Countries are.

> This is why the paper says conditional estimate, not treatment effect.

---

## Slide 8 — What fails (7:15–8:15)

**On slide**
- Daily design: Δspread on ΔP
- β ≈ 0, |t| < 1, with and without controls
- Cause: of 257 prints, only **two** move more than 10 pp
- Both artefacts: opening week, and a print 10 days *after* the result
- **No dose–response, so the DiD is binary, not intensity-based**

**Say**
> The design I originally wanted was to regress daily changes in the spread on daily changes in the probability. It does not work, and I show why rather than hide it.

> Of 257 prints, only two move by more than ten points: plus 19.5 on a Saturday in the contract's first week, when liquidity was being discovered, and plus 31 on 22 April, ten days after the election, when the contract had stopped trading on news. Everything else is noise of a few points.

> So the treatment variable is flat through the campaign and then jumps when the outcome is known. There is no intensity to exploit. That is why the DiD uses a date, not a price.

---

## Slide 9 — The finding I did not expect (8:15–9:20) — **Figure 6**

**On slide**
- Back out the probability implied by the spread
- 9 April, three days before the vote:
  - Polymarket: **69%**
  - Bonds: **35%**
- Both reach 100% only afterwards

**Say**
> If the spread moves linearly with the probability of regime change, I can invert it and ask what probability bonds were implying. It is a crude device — a rescaled spread, not an independent estimate — but it is informative.

> Three days before the vote, the prediction market had priced 69 per cent. The bond market had priced about a third. They did not disagree about the level of risk; they disagreed about when to price it.

> A market that asks about the event directly moved weeks ahead of one that prices it only through a risk premium.

---

## Slide 10 — Conclusion (9:20–10:00)

**On slide**
- DiD: **−109 bp** on the election window, 1 of 8 countries
- 65% of it after the result, not before
- Prediction market led by weeks
- Limits: pre-trend, p = 0.125, one treated unit
- What would settle it: more elections, panel of prediction markets

**Say**
> To summarise: Hungarian sovereign risk fell by about 109 basis points relative to its neighbours around a regime change — 157 if you compare endpoints — most of it after the result rather than before, and the prediction market knew first.

> The estimate is conditional. The leads are jointly non-zero, inference has a floor at one in eight, and there is one treated country. What would settle it is the same exercise across several elections — Poland 2023, Slovakia 2023 — where the treatment dates differ and the randomisation test has more than eight assignments.

Thank you.

---

# Q&A — prepared answers

**"Your joint pre-trend test rejects. Doesn't that kill the DiD?"**
> It rejects that the leads are *exactly* zero, which at three hundred observations a month is a weak test — 0.1 points is precise. What would be fatal is a lead that trends, because a trend control cannot absorb a trend. There is none, and the proof is that all three trend treatments agree to five basis points. A reader who wants no trend assumption at all should read −1.04 instead of −1.09.

**"Why start in 2024? Isn't that just choosing your sample?"**
> Because the placebo dates say so. On 2022 data the same design returns −1.1 at essentially every fake date, which means it is measuring the 2022 disinflation convergence rather than an election. On 2024 data every fake date returns zero. The restriction costs me nothing: the no-trends estimate *falls* from −1.46 to −1.04 when 2022 is dropped.

**"Your t-statistic is −11. Why do you then say p = 0.125?"**
> Because they measure different things. Driscoll–Kraay asymptotics count time periods, and I have 3,040 of them. The design has one treated unit, and with eight units there are eight possible assignments. Days are not the constraint; countries are. Reporting the t-statistic alone would be the most misleading thing in the paper.

**"Isn't this just the EU funds story?"**
> Possibly, and I cannot separate the two. EU funds and political risk both predict a long-end compression, and both arrive in the same weeks, so they are observationally equivalent here. That is a limitation of one treated unit, not something a control group fixes.

**"Why not synthetic control?"**
> Six donors is too few for a credible counterfactual, and Hungary's yield level sits outside the convex hull of its neighbours for most of the pre-period. The DiD with country trends is the honest compromise.

**"Is Polymarket reliable? It's banned in Hungary."**
> No. It is thin, manipulable, and its users are self-selected foreign observers. I use it as a proxy for a probability, never as truth. The lead–lag result only needs the two series measured consistently, not for Polymarket to be right.

**"What is the single biggest threat?"**
> That the compression was the National Bank's easing cycle. The term structure argues against it: before the vote the ten-year fell 40 basis points while the five-year rose 13. Easing moves the short end. This moved the long end.

---

# Numbers card — memorise these six

| | |
|---|---|
| DiD, kinked trend, to inauguration | **−109 bp** |
| DiD, no trend / linear | −104 / −109 bp |
| Own yield fall | −138 bp |
| Pre-vote / post-result split | 35 / 65 |
| Randomisation inference p | 0.125 (floor of 1/8) |
| 9 April: Polymarket vs bonds | 69% vs 35% |
