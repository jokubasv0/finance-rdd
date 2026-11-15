# Pricing Regime Change — 10-minute talk

Total: 9 slides, 9 min 45 s. Leave 15 s buffer.

Rule for the whole talk: **say the number, then say what it means.** Never read a table.

---

## Slide 1 — Title (0:00–0:40)

**On slide**
- Pricing Regime Change: Hungary's 2026 Election and Sovereign Risk
- One question: *did markets price the fall of a government before it fell?*
- Daily data, July 2025 – November 2026

**Say**
> On 12 April 2026 Viktor Orbán lost an election he had been expected to win. Hungary's ten-year yield had already fallen by the time he conceded. The question is not whether yields fell — they did — but whether the movement was about Hungarian politics at all, and when the market learned.

---

## Slide 2 — Why this case (0:40–1:40)

**On slide**
- 16 years in office, supermajority, EU funds frozen
- One country, one election, one clean date
- A prediction market existed and traded $101 million on it

**Say**
> Hungary is unusually good for this question. Sixteen years of one government means the election is a genuine regime risk, not a rotation. EU cohesion funds were frozen, so the result had a direct fiscal consequence. And uniquely, there was a liquid prediction market on the exact event — 101 million dollars of volume on who becomes prime minister.

That last point is the reason this paper can exist. Normally we infer what markets believed from prices. Here we can observe a direct probability, daily.

---

## Slide 3 — Data (1:40–2:40)

**On slide**
- Polymarket: P(Orbán not PM), daily, 197 prints
- Ten-year yields: HU, CZ, PL, RO, SI, HR, AT, DE
- Also 5Y, EUR/HUF, US 10Y, VIX, Brent
- Window: 25 Jul 2025 → 8 May 2026, 194 trading days

**Say**
> Everything is free and public. Yields come from Investing.com, the probability from Polymarket's own API, and the global controls from Yahoo Finance.

The control group matters. My first draft compared Hungary only to Czechia. That was a mistake I want to flag early, because Czechia turns out to be the most generous possible control — Czech yields rose 47 basis points over the window while Hungary's fell 138. So the paper uses the average of six central European peers instead, and reports Czechia as an upper bound.

---

## Slide 4 — The result (2:40–4:00) — **Figure 1**

**On slide**
- HU 10Y: 7.13 → 5.75 (**−138 bp**)
- HU − peer average: −157 bp
- HU − Bund: −167 bp
- **Hungary is the only one of eight countries whose yield fell**

**Say**
> Here is the raw fact. Between July 2025 and May 2026 the Hungarian ten-year fell 138 basis points. Every peer went the other way or stayed flat. Relative to the peer average the compression is 157 basis points — that is the headline number.

Point at the chart: the red line is Hungary, the blue is the peer average.

> The divergence is not gradual. It opens in two steps, and that shape is the whole paper.

---

## Slide 5 — When it happened (4:00–5:10)

**On slide**
| Window | HU − peers |
|---|---:|
| Pre-campaign, to 26 Feb | −39 |
| Campaign, to 9 Apr | −17 |
| **Before the vote** | **−56 (35%)** |
| Result to inauguration | **−102 (65%)** |

**Say**
> Splitting the window at the vote gives 35 per cent before, 65 per cent after. That is the opposite of what I expected, and it is the opposite of what the Czech-only control suggested.

Two independent methods agree on this split: the peer average and a market model that predicts Hungarian yields from Czech, Polish, Romanian, US and global factors. Both say roughly a third before, two thirds after.

Why does it matter? Because it kills the simplest story. If the market had fully priced the result in advance, the vote itself would be a non-event. It wasn't.

---

## Slide 6 — Is it Hungary or the region? (5:10–6:20) — **Table 4 / placebo figure**

**On slide**
- Same calculation, each country in turn: HU −157
- Next largest deviation: Romania −48, Czechia +33
- Placebo dates: 204 random windows
- **15% of random windows are at least this negative**

**Say**
> Two checks. First, I ran the same calculation treating each country as if it were the event. Hungary's deviation is more than three times the largest peer's. The region did not move together, so this is not a Central European risk-appetite story.

Second, the honest one: I drew 204 random 194-day windows from 2022 to 2025 and computed the same statistic. One window in seven is at least as large as the real one. So the magnitude is large but not statistically unusual for this series.

That is a limitation, and I would rather say it than have it said to me.

---

## Slide 7 — What fails (6:20–7:30)

**On slide**
- The obvious regression: Δspread on ΔP
- β ≈ 0, |t| < 1, with or without controls
- Cause: the probability moves twice, both times uninformative
- **No dose-response, so no causal claim**

**Say**
> The design I wanted was to regress daily changes in the spread on daily changes in the probability. It does not work, and I want to show you why rather than hide it.

Of 197 prints, only two move by more than ten points: plus 20 in the contract's first week, when liquidity was being discovered, and plus 31 on 22 April — ten days after the election, when the contract had stopped trading on news. Everything else is noise of a few points.

So the treatment variable is essentially flat for the entire campaign, then jumps when the outcome is already known. There is no dose-response to estimate. I report a null and I do not dress it up.

---

## Slide 8 — The finding I did not expect (7:30–8:50) — **Figure 6**

**On slide**
- Back out probability implied by the bond spread
- 9 April, three days before the vote:
  - Polymarket: **69%**
  - Bonds: **35%**
- Both reach 100% only afterwards

**Say**
> If I assume the spread moves linearly with the probability of regime change, I can invert it and ask what probability the bond market was implying. That is a crude device — it is a rescaled spread, not an independent estimate — but it is informative.

On 9 April, three days before the vote, the prediction market had priced 69 per cent. The bond market had priced about a third. Neither was wrong about the level of risk; they disagreed about the timing of information.

This is the paper's most interesting result. A prediction market, which asks about the event directly, moved about six weeks ahead of a bond market, which prices it only through the risk premium.

---

## Slide 9 — Conclusion (8:50–9:45)

**On slide**
- Markets repriced Hungarian risk by ~157 bp
- Two thirds of it after the result, not before
- Prediction markets led bond markets by weeks
- **Descriptive, not causal — one country, one event**
- What would change my mind: a second country, or intraday poll windows

**Say**
> To summarise: the repricing was large, it was Hungary-specific, and most of it came after the result rather than before.

The contribution is measurement, not identification. With one treated country I cannot rule out that something else happened in Hungary in those nine months. What would settle it is the same exercise on more elections — Poland 2023, Slovakia 2023 — or intraday windows around poll releases.

The honest one-line version: **Hungarian sovereign risk fell by about 157 basis points relative to its neighbours around a regime change, and prediction markets knew before bond markets did.**

Thank you.

---

# Q&A — prepared answers

**"Isn't this just the EU funds story?"**
> Possibly, and I cannot separate them. EU funds are part of the same political package and may well have moved in the same window; if they did, the two are consequences of one cause and no regression on my data separates them. That is a limitation of one treated unit, not something a control group fixes.

**"Why not synthetic control?"**
> I tried the donor pool. Six peers is too few for a credible synthetic counterfactual, and the pre-period fit was poor because Hungary's yield level was outside the convex hull of its neighbours. The peer average is the honest compromise.

**"Your t-statistics are all insignificant."**
> Correct, and that is the finding. With 194 daily observations and a treatment that jumps twice, there is no statistical power. I report the null rather than a specification that happens to clear 1.96.

**"Is Polymarket reliable? It's banned in Hungary."**
> No. It is thin, manipulable, and its users are not representative. I use it as a proxy for a probability, never as truth, and the paper says so. The lead-lag result only needs the two series to be measured consistently, not for Polymarket to be right.

**"What is the single biggest threat?"**
> That the compression was driven by the National Bank's easing cycle. The term structure argues against it: before the vote the ten-year fell 40 basis points while the five-year rose 13. Rate-cut expectations move the short end. This moved the long end.

**"Why does 15% matter?"**
> It means I cannot reject that this window is drawn from the normal distribution of Hungarian spread changes. The magnitude is unusually large; the evidence is not statistically unusual. Both statements are in the paper.

---

# Numbers card — memorise these six

| | |
|---|---|
| Headline spread compression | **−157 bp** |
| Own yield fall | −138 bp |
| Pre-vote / post-result split | 35 / 65 |
| Hungary's rank among 8 countries | 1 (only faller) |
| Placebo-date p-value | 0.15 |
| 9 April: Polymarket vs bonds | 69% vs 35% |
