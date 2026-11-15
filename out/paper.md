# Who Prices Regime Change First?

## Prediction Markets, Sovereign Spreads, and Hungary's 2026 Election

---

## Abstract

On 12 April 2026 Hungary elected a government that ended sixteen years of Fidesz rule. Using daily data on eight Central European sovereign bond markets and the full price history of a $101 million Polymarket contract on whether Viktor Orbán would remain prime minister, we document two facts. First, Hungary's ten-year yield fell 138 basis points over the nine months surrounding the election while every other Central European yield rose or was flat, compressing Hungary's spread over a six-country peer average by 157 basis points. Hungary is the only one of eight countries whose yield fell. Two-thirds of that compression occurred after the result, and the pre-election part was driven by the long end while the short end rose — the opposite of what monetary easing would produce. Second, prediction markets and bond markets disagreed about timing: three days before the vote Polymarket had priced 69 per cent of the eventual move while the bond spread had priced about 35 per cent. The prediction market moved first and the bond market followed. We are careful about what this does not show. The daily relationship between the probability series and the spread is indistinguishable from zero, random-date placebo windows reproduce the spread compression 15 per cent of the time, and with one treated country conventional inference is unavailable. The paper is therefore descriptive: it establishes the magnitude, the timing, and the cross-country uniqueness of the repricing, and it identifies a lead–lag pattern between two markets that has not previously been documented for a European regime change.

**JEL codes:** G12, G14, G15, H63, P16

**Keywords:** sovereign spreads, prediction markets, political risk, regime change, Central Europe

---

## 1. Introduction

Sovereign bond markets are supposed to price political risk. When voters can remove a government, the probability of that removal should be embedded in the yield investors demand. Yet the empirical record on whether this happens — and when — is thin. Most studies of elections and asset prices look at equity markets in advanced economies, where political risk is small and the event is short. Studies of emerging-market sovereign spreads usually work at monthly or quarterly frequency, which is too coarse to separate anticipation from realisation.

Hungary's April 2026 election is an unusually clean case for looking at this directly. Three features make it useful.

First, the outcome was a genuine regime change, not a rotation. Fidesz had governed since 2010. The election produced a Tisza supermajority of 141 seats, and Péter Magyar was sworn in on 9 May 2026. A change of this size is the kind of event that should move a risk premium.

Second, the election was heavily traded in a prediction market. Polymarket ran a contract on whether Orbán would be the next prime minister, which traded $25.5 million inside a $101.1 million event and ran from July 2025 to April 2026. That gives a daily, forward-looking measure of the market's belief about the outcome, which is exactly the variable a bond investor would need.

Third, Hungary has close, liquid comparators. Czechia, Poland, Romania, Slovenia, Croatia and Austria all issue euro- or local-currency benchmarks with daily quotes. A spread against those peers strips out the global and regional component of the yield move, which is the dominant source of variation in a nine-month window.

We use these three features to ask two questions. How large was the Hungary-specific repricing, and when did it happen? And did the prediction market, which is a direct measure of the probability of regime change, lead or lag the bond market, which is an indirect one?

The answers are as follows.

Hungary's ten-year yield fell from 7.13 to 5.75 per cent between 25 July 2025 and 8 May 2026, a decline of 138 basis points. Over the same window the six-country peer average rose 19 basis points, the German yield rose 29, and the Czech yield rose 47. Hungary's spread over the peer average fell from 274 to 116 basis points, a compression of 157 basis points. Hungary is the only one of the eight countries whose yield fell, and in a placebo exercise that treats each country in turn as the candidate event, Hungary's spread deviation is more than three times the largest peer's.

The compression is not evenly distributed in time. Splitting the window at the election, 56 basis points — about 35 per cent — occurred before the vote and 102 basis points — about 65 per cent — occurred between the result and the inauguration. This matters because the earlier version of this literature, and our own first pass at the data, treated the pre-election move as the whole story. It is not. The larger part came after the outcome was known.

The pre-election component is also not a monetary-policy story. Between July 2025 and early April 2026 the Hungarian ten-year yield fell 40 basis points while the five-year yield *rose* 13. The curve flattened by 53 basis points. Rate-cut expectations move the short end first and the long end less; a fall in the long end combined with a rise in the short end is a term-premium story, not an easing story.

Then the timing comparison. Using the realised spread compression as the terminal value, we can back out an implied probability of regime change from bond prices at each date, and compare it with the Polymarket probability. On 25 July 2025 both were near zero by construction. By 26 February 2026 Polymarket had reached 63 per cent while bonds implied 25 per cent. By 9 April, three days before the vote, Polymarket had reached 69 per cent and bonds implied 35 per cent. After the result the two converged. The prediction market consistently led.

That lead is the paper's most original observation, and it is also the reason the paper's title is a question rather than a claim about causality.

We are explicit about the limits. The natural next step — regressing daily spread changes on daily changes in the probability — does not work. The estimated coefficient is statistically indistinguishable from zero in every specification we tried, because the probability series has essentially two large prints, both of which are artefacts of contract mechanics rather than news. Random-date placebo windows in the pre-election sample are at least as negative as the actual window 15 per cent of the time, which means the aggregate cannot be distinguished from ordinary spread volatility at conventional levels. And with a single treated country there is no credible source of random variation in treatment, so no standard error we could report would mean what it appears to mean.

What survives is a set of descriptive claims that are strong on magnitude, strong on cross-country comparison, and honest about inference. The contribution is to show that a European regime change produced a large, country-specific, long-end sovereign repricing that was concentrated after the result, and that a prediction market anticipated it by roughly three weeks. That lead–lag pattern is, as far as we are aware, undocumented for a European election.

The remainder of the paper is organised as follows. Section 2 gives the institutional background. Section 3 describes the data. Section 4 sets out what we do and, importantly, what we do not. Section 5 presents results. Section 6 reports the tests that fail. Section 7 discusses robustness. Section 8 discusses limitations and Section 9 concludes.

---

## 2. Institutional background

Hungary held parliamentary elections on 12 April 2026. Fidesz–KDNP, in office since 2010, was defeated by the Tisza party led by Péter Magyar, which won a supermajority of 141 seats. Magyar was sworn in as prime minister on 9 May 2026.

Three background conditions shape how the market should have reacted.

**Fiscal and external vulnerability.** Hungary entered the election with one of the highest sovereign spreads in the region and a large gross financing need. Its ten-year yield stood at 7.13 per cent in July 2025 against a peer average of 4.39, a spread of 274 basis points. This is a country where the risk premium is large enough that a change in perceived political risk has room to move.

**EU funds.** A substantial portion of Hungary's EU cohesion and recovery funding was withheld during the period on rule-of-law conditionality. The expectation that a change of government would unlock those funds is a plausible channel through which the election could lower sovereign risk, independently of any change in fiscal policy.

**Monetary policy.** The Magyar Nemzeti Bank was in an easing cycle through part of the sample. This is the main confounder, and Section 5.4 addresses it directly using the term structure.

The prediction market ran from 24 July 2025 to 12 April 2026. Its opening print put Orbán's probability of remaining prime minister at 61.5 per cent. The contract resolved to zero after the result.

---

## 3. Data

### 3.1 Sovereign yields

Daily ten-year benchmark yields for eight countries — Hungary, Czechia, Germany, Poland, Romania, Slovenia, Croatia and Austria — from Investing.com's historical data API, 1 June 2025 to 13 November 2026, with a longer 2022–2026 series for the five countries with continuous coverage (Hungary, Czechia, Germany, Poland, Romania). Hungarian five-year yields are from the same source.

Two-year Hungarian yields are not available from this source; this is a limitation discussed in Section 8. The five-year series is used instead, which is a weaker but still informative test of the term-structure mechanism.

### 3.2 Prediction market

The full daily price history of the Polymarket contract "Will the next Prime Minister of Hungary be Viktor Orbán?", retrieved from the CLOB prices-history endpoint. The series contains 197 prints over 287 calendar days. We define the treatment variable as

$$P_t = 1 − Price(Orbán next PM)_t$$

the market-implied probability that Orbán does not remain prime minister.

Two properties of this series must be stated plainly because they drive the results in Section 6. First, the contract prints only on days on which it trades. Second, it has essentially two large jumps: +20.0 percentage points on 27 July 2025, in the first days of the contract's life, and +30.9 percentage points on 22 April 2026, ten days after the election, when the outcome was already known. Neither is news about Hungarian politics.

### 3.3 Control variables

US ten-year yield, VIX, Brent crude, and EUR/USD from Yahoo Finance. EUR/HUF is constructed as USD/HUF × EUR/USD.

### 3.4 Sample construction

The event window runs from 25 July 2025, the first day the prediction market has a price, to 8 May 2026, the day before the new government took office. This gives 194 trading observations. The estimation sample for the market model runs from 4 January 2022 to 30 June 2025, 839 observations, ending before the window opens.

The peer average is the equal-weighted mean of Czech, Polish, Romanian, Slovenian, Croatian and Austrian ten-year yields, requiring at least four non-missing observations. The primary spread is

$$S_t = y(HU)_t − ȳ(peers)_t$$

We report the Bund spread and the Czech spread alongside it throughout, because the choice of control turns out to matter and we do not want to hide that.

---

## 4. Empirical strategy

The paper is descriptive. We state this at the outset rather than presenting a causal design and then retreating from it, because the retreat would be necessary and it is better to be explicit.

The evidence is organised in four blocks, each of which answers a different question.

**Block 1 — magnitude.** The change in the Hungary–peer spread over the window, decomposed into sub-windows at the election. This is arithmetic, not estimation.

**Block 2 — uniqueness.** The same calculation for every country in the sample, treating each in turn as the "treated" unit and the others as controls. If the Hungarian move is political, it should be large relative to the distribution of peer moves.

**Block 3 — mechanism.** The term structure. If the compression reflects a lower risk premium, it should be concentrated at the long end. If it reflects expected rate cuts, it should be concentrated at the short end.

**Block 4 — timing.** A comparison of the probability implied by Polymarket with the probability implied by the bond spread, where the latter is backed out as

$$π_t = (S₀ − S_t) / (S₀ − S_T)$$

with the initial spread S₀ taken on 25 July 2025 and the terminal spread taken on 8 May 2026. This is a linear interpolation along the path, and it assumes the spread would not have moved absent the election. It is a descriptive device, not an estimate.

What we do not do is estimate a treatment effect. Section 6 explains why the obvious design — daily changes in the spread on daily changes in the probability — fails, and Section 8 explains why no repair is available with one treated country.

---

## 5. Results

### 5.1 The compression

Table 1 reports ten-year yields at the start and end of the window for all eight countries.

**Table 1. Ten-year yields, 25 July 2025 to 8 May 2026 (per cent)**

| Country | 25 Jul 2025 | 8 May 2026 | Change (bp) |
|---|---:|---:|---:|
| **Hungary** | **7.13** | **5.75** | **−138** |
| Czechia | 4.32 | 4.79 | +47 |
| Poland | 5.50 | 5.60 | +10 |
| Romania | 7.23 | 7.02 | −21 |
| Germany | 2.72 | 3.00 | +29 |
| Slovenia | 3.12 | 3.41 | +29 |
| Croatia | 3.14 | 3.45 | +31 |
| Austria | 3.06 | 3.25 | +20 |
| Peer average | 4.39 | 4.59 | +19 |

Hungary is the only country in the table whose yield fell by more than 21 basis points. The global backdrop was a bear steepening: German, Austrian, Slovenian and Croatian yields all rose by 20 to 31 basis points. The Hungarian move is therefore not a global duration effect. It is the opposite of one.

The spread consequences are in Table 2.

**Table 2. Hungary spreads, 25 July 2025 to 8 May 2026 (percentage points)**

| Spread | 25 Jul 2025 | 8 May 2026 | Change (bp) |
|---|---:|---:|---:|
| HU − peer average | 2.74 | 1.16 | **−157** |
| HU − peer median | 3.40 | 1.63 | −177 |
| HU − Bund | 4.41 | 2.75 | −167 |
| HU − Czechia | 2.81 | 0.96 | −185 |

The headline is −157 basis points against the peer average. Against Czechia alone the number is −185. We use the peer average as the primary measure because Czechia is the most favourable single control, as Section 5.3 shows, and because a single-country control cannot distinguish a Hungarian shock from a Czech one.

Figure 1 plots the three series. Figure 2 plots the Hungary–peer spread over the full 2022–2026 period, which shows that the compression is not a continuation of a pre-existing trend but a discrete break.
![](fig1_levels.png)

**Figure 1.** Ten-year sovereign yields: Hungary, the six-country peer average, and Germany, July 2025 to November 2026. Vertical lines mark the start of the campaign, election day and the inauguration.

![](fig2_spread.png)

**Figure 2.** Hungary's spread over the peer average, 2022 to 2026. The 2026 compression is a break rather than a continuation of the earlier trend.


### 5.2 Timing

Table 3 decomposes the window at the election.

**Table 3. Event-window decomposition (basis points)**

| Window | HU − peers | HU − Bund | HU − CZ | HU 10Y |
|---|---:|---:|---:|---:|
| A. 25 Jul 2025 → 26 Feb 2026 (pre-campaign) | −39 | −62 | −68 | −64 |
| B. 26 Feb → 9 Apr 2026 (campaign) | −17 | −7 | −19 | +24 |
| **A + B. Pre-vote** | **−56** | **−69** | **−86** | **−40** |
| C. 9 Apr → 8 May 2026 (result to inauguration) | −102 | −97 | −99 | −98 |
| **Total** | **−157** | **−167** | **−185** | **−138** |

Against the peer average, 35 per cent of the compression happened before the vote and 65 per cent after the result. Against Czechia the split is closer to half and half. This is a substantive difference and it is the reason we moved away from the Czech control: Czech yields rose 47 basis points over the window while the peer average rose only 19, so Czechia mechanically produces a larger and earlier-looking Hungarian effect. The peer average and the market-model residual in Section 5.3, which are constructed independently, agree on roughly a 35/65 split. Czechia does not.

The campaign window B is the weakest part of the story. Hungarian yields *rose* 24 basis points in nominal terms between late February and early April, even as the probability of regime change rose. Against peers the spread narrowed only 17 basis points. Whatever was happening in the campaign, it was not a clean monotone repricing of political risk.

### 5.3 Was it Hungary-specific?

Table 4 treats each country in turn as the treated unit, computing its spread against the average of the other six.

**Table 4. Country placebo, same window (basis points)**

| Country | Spread change vs others |
|---|---:|
| **Hungary** | **−157** |
| Romania | −48 |
| Poland | −11 |
| Austria | 0 |
| Slovenia | +12 |
| Croatia | +14 |
| Czechia | +33 |

Hungary's deviation is more than three times the largest peer deviation. If the compression were a regional risk-appetite story, we would expect the peers to move together and in the same direction. They do not.

The choice of control also matters less than one might fear. Table 5 shows the Hungarian spread against every possible control.

**Table 5. Control-choice sensitivity (basis points, same window)**

| Control | Spread change | Daily t-statistic |
|---|---:|---:|
| Czechia | −185 | −1.91 |
| Peer median | −177 | −0.79 |
| Croatia | −169 | −1.57 |
| Germany | −167 | −1.48 |
| Slovenia | −167 | −1.66 |
| Austria | −158 | −1.39 |
| **Peer average** | **−157** | **−1.71** |
| Poland | −148 | −1.25 |
| Romania | −117 | −0.93 |

Every control produces a large negative number. The range is −117 to −185. The sign is robust; the magnitude is not, and the daily t-statistics are between −0.9 and −1.9, which is to say nothing is significant at conventional levels. We report this rather than the most favourable number.

An independent construction gives a similar answer. We estimate a market model on 2022–2025 data,

$$Δy(HU)_t = α + β₁ Δȳ(CEE)_t + β₂ Δy(US)_t + β₃ ΔVIX_t + β₄ Δln Brent_t + ε_t$$

where CEE3 is the Czech–Polish–Romanian average. The fit is reported in Table 6.

**Table 6. Market model, 4 Jan 2022 – 30 Jun 2025**

| Variable | Coefficient | t-statistic |
|---|---:|---:|
| Constant | 0.0007 | 0.19 |
| ΔCEE3 | 0.9160 | 8.43 |
| ΔUS 10Y | 0.1286 | 1.65 |
| ΔVIX | 0.0011 | 0.37 |
| Δ ln Brent | 0.1089 | 0.48 |
| N | 841 | |
| R² | 0.248 | |

The Hungarian yield moves almost one-for-one with its regional peers once the peer average is measured on a constant composition, which is what one expects of a small open economy in a common currency-area periphery. The cumulative Hungary-specific residual — the part of the yield move not explained by regional, US, volatility or commodity factors — is −7 basis points by December 2025, −22 by 26 February 2026, −57 by 9 April, and −162 by 8 May. That is a 35/65 pre/post split, matching the peer average almost exactly and inconsistent with the Czech-only control. Figure 3 plots the residual path.
![](fig3_residual.png)

**Figure 3.** Cumulative Hungary-specific residual from the market model of Table 6.


### 5.4 Not monetary policy

The main confounder is the National Bank of Hungary's easing cycle. If the yield fell because rate cuts were expected, the compression should be concentrated at the short end of the curve. Table 7 shows the opposite.

**Table 7. Hungarian term structure (basis points)**

| | 25 Jul 2025 | 9 Apr 2026 | 8 May 2026 |
|---|---:|---:|---:|
| 10Y yield | 7.13 | 6.73 | 5.75 |
| 5Y yield | 6.55 | 6.68 | 5.64 |
| 10Y − 5Y slope | +58 | +5 | +11 |

Between July 2025 and 9 April 2026 the ten-year yield fell 40 basis points while the five-year yield rose 13. The slope flattened by 53 basis points. Rate-cut expectations cannot produce a fall in the long end and a rise in the short end simultaneously; the standard transmission runs the other way. A fall in the long end with a rise in the short end is a compression of the term premium, which is what a reduction in political risk should look like.

After the result the move becomes parallel: the ten-year fell 98 basis points and the five-year fell 104, so the slope was roughly unchanged at +6 basis points. This is consistent with a broad repricing of Hungarian risk rather than a change in expected policy rates.

Figure 5 plots the slope. It is worth noting that the flattening began before the campaign and is visible from late 2025, which is consistent with the pre-election component of the spread compression identified in Table 3.

![](fig5_slope.png)

**Figure 5.** Hungarian 10Y minus 5Y slope, July 2025 to November 2026.


### 5.5 Prediction market versus bond market

Table 8 backs out the probability of regime change implied by the bond spread, using the realised 8 May spread as the terminal value, and compares it with Polymarket.

**Table 8. Implied probability of regime change**

| Date | Spread (pp) | Polymarket P | Bond-implied P |
|---|---:|---:|---:|
| 25 Jul 2025 | 2.74 | 0.385 | 0.000 |
| 26 Feb 2026 | 2.35 | 0.625 | 0.245 |
| 9 Apr 2026 | 2.18 | 0.685 | 0.354 |
| 8 May 2026 | 1.16 | 1.000 | 1.000 |

The divergence is substantial and one-directional. Polymarket reached 63 per cent by late February while bonds had priced 25 per cent. By 9 April the gap was 69 against 35. Bonds caught up only after the result.

This is the paper's central descriptive finding. A prediction market, which asks directly about the event, moved roughly six weeks ahead of a bond market, which prices the event only indirectly through the risk premium. The two markets were not disagreeing about the *level* of risk — they both ended at 1.0 — but about *when* to price it.

Two caveats apply. The bond-implied series is a linear interpolation, so it is not an independent estimate of the probability; it is a rescaled spread. And the terminal value is the realised spread, which is itself an outcome. If the post-election spread compression contained a component unrelated to the election, the bond-implied probability is overstated at every date, which would *narrow* the gap and weaken the finding. We cannot rule this out.

Figure 6 plots the two series.
![](fig6_implied.png)

**Figure 6.** Polymarket implied probability of regime change against the bond-implied probability from Table 8.


### 5.6 What happened afterwards

The window closes at the inauguration, but the data run to November 2026. Hungary's ten-year yield fell further to 5.09 per cent by 30 June, rose to 5.64 by 31 August, and stood at 5.52 on 13 November. The peer spread continued to compress, from 116 basis points in May to 69 in June, 83 in August and 51 in November — a further 65 basis points.

This is important for interpretation. The compression did not reverse. If the May 2026 spread level had been a temporary overreaction, we would expect mean reversion; the continued narrowing suggests the market was repricing a persistent change in Hungarian risk rather than overshooting. EUR/HUF, meanwhile, appreciated 3.0 per cent after the inauguration, having already gained 10.3 per cent over the window.

---

## 6. What does not work

We report three failed tests, in order of how much damage they do.

### 6.1 The daily dose–response regression

The natural design regresses daily changes in the spread on daily changes in the probability:

$$ΔS_t = α + β ΔP_t + γ′ΔX_t + ε_t$$

with β < 0 expected. It does not work. Without controls, $\hat\beta = +0.007$ with a t-statistic of 0.12 over 193 observations. With controls, $\hat\beta = -0.047$, t = −0.75 over 184. The coefficient is indistinguishable from zero, and its sign is not stable across the two specifications.

The reason is visible in the probability series itself. Of 197 prints, only two move by more than 10 percentage points: +20.0 on 27 July 2025 and +30.9 on 22 April 2026. Only five move by more than 5. The first of the two is the contract's opening-week liquidity discovery, when the implied probability moved from 0.385 to 0.585 in four days while the Hungarian spread did not move at all. The second occurred ten days after the election, when the contract had already stopped trading on news. Everything else is noise of a few percentage points.

A treatment variable with two effective observations, both of which are mechanical artefacts, cannot support a dose–response estimate. We report the regression because a reader will ask for it, not because it supports the paper.

### 6.2 Random-date placebos

We draw 204 random 194-day windows from the 2022–2025 Hungary–(CZ, PL, RO) spread series, excluding the actual window. The distribution has mean −29 basis points, standard deviation 98, minimum −212, maximum +278. The actual window's −150 basis points lies at the 15th percentile. Fifteen per cent of arbitrary windows in the pre-election sample are at least as negative.

For a single-country event study this is the binding constraint. It means the aggregate compression, taken alone, cannot be distinguished from ordinary spread volatility. What rescues the analysis is not the size of the number but its cross-country uniqueness (Table 4) and its timing relative to the probability series (Table 8). Magnitude alone is not enough.

Figure 4 plots the distribution.
![](fig4_placebo.png)

**Figure 4.** Distribution of 194-day spread changes from 204 random start dates in 2022 to 2025, with the actual window marked.


### 6.3 Inference with one treated unit

There is no credible standard error for a one-country event study. Clustered standard errors require a number of clusters; randomisation inference over seven countries has a minimum attainable p-value of 1/7 ≈ 0.14. Any t-statistic we could report for the −157 basis point estimate would be a decoration.

We therefore do not report one, and we do not describe the design as a difference-in-differences. A specification with country and date fixed effects, one treated unit and a continuous treatment is algebraically the treated unit's idiosyncratic series regressed on the treatment, which is a two-point slope. Calling it DiD would invite a correction in question time that the paper cannot survive.

---

## 7. Robustness

**Alternative controls.** Table 5. Every control gives −117 or larger in absolute value.

**Trend adjustment.** The Hungary–(CZ, PL, RO) spread was already narrowing before the election. Fitting a linear trend to 2022-01 to 2025-06 gives −0.086 basis points per trading day, or −22 basis points per year. Over a 194-day window the trend predicts −17 basis points of compression. Subtracting gives a trend-adjusted estimate of **−133 basis points**. The honest range for the headline is therefore −133 to −157.

**Alternative terminal dates.** Using 13 November 2026 rather than 8 May 2026 as the terminal point increases the spread compression to −223 basis points, but that window includes five months of post-election policy. We prefer the narrower window and report the wider one only as evidence that the compression did not reverse.

**Excluding the contract's opening week.** Dropping 25 July to 1 August 2025 removes the first artefactual probability jump and reduces the pre-election component to about −20 basis points, which strengthens rather than weakens the 65/35 post/pre split.

**Alternative peer definitions.** Equal-weighted average, median, Bund-only and Czech-only are all reported in Tables 2 and 5. The sign is invariant.

**Regional shock check.** On 19 March 2026 the Hungarian spread widened sharply, reaching 258 basis points against Czechia. Inspection of the cross-section shows this was a regional selloff: Romanian yields rose 31 basis points that day, Croatian 22, Hungarian 19, Slovenian 15, Polish 7, Czech 4 and German 1. Against the peer average Hungary moved 4 basis points. This is a common shock, not a Hungarian event, and it illustrates why a single-country control is fragile and why the peer average is the better measure.

---

## 8. Limitations

**One treated unit.** This is the fundamental constraint. Everything else follows from it. With a single country there is no treatment variation that can be used to construct a counterfactual, and no inference that is not essentially illustrative. The paper's claims are therefore about what happened, not about what caused it.

**The probability series is mechanically contaminated.** Two of the 197 prints account for most of the variance and both are artefacts. A better treatment variable would be built from polling data, which is available at higher frequency and does not suffer from liquidity discovery. We did not build one, and the paper's lead–lag result would be stronger if we had.

**No Hungarian two-year yield.** The term-structure test uses the five-year point, which is an imperfect substitute. A two-year series would sharpen the distinction between expectations and term premium. The data exist at the National Bank of Hungary but not in the machine-readable source used here.

**The bond-implied probability is not independent.** It is a rescaled spread, so the comparison in Table 8 is between one market price and a monotone transformation of another. The finding is about timing, not about two independent estimates agreeing or disagreeing.

**Polymarket is not a representative survey.** The contract is thin relative to the bond market, tradeable only outside Hungary, and its participants are self-selected. Its price is a proxy for market belief, not a measure of it. The contract was also effectively closed to Hungarian residents, which may bias the participant pool toward foreign observers.

**Confounders we cannot separate.** EU funds, fiscal announcements, and changes in the National Bank's reaction function all moved during the window. We control for none of them directly. The term-structure evidence rules out a pure rate-expectations explanation but does not rule out an EU-funds explanation, and in fact the two are complementary: both predict a long-end compression.

**External validity.** One election in one country. Whether prediction markets lead bond markets in general is not something this paper can establish.

---

## 9. Conclusion

Hungary's 2026 election coincided with a 157 basis point compression in its sovereign spread over a six-country peer average. Hungary was the only one of eight Central European countries whose ten-year yield fell. Two-thirds of the compression occurred after the result rather than before it. The pre-election component was concentrated at the long end of the curve, which rules out a rate-expectations explanation.

A prediction market on whether Orbán would remain prime minister moved ahead of the bond market, reaching 69 per cent by three days before the vote while bonds had priced about 35 per cent of the eventual move.

The paper cannot show that the election caused the repricing. Random-date placebos reproduce a compression of this size 15 per cent of the time, the daily relationship between the probability series and the spread has the wrong sign, and there is one treated country. These are not caveats appended to a causal claim; they are the reason the claim is descriptive.

What the paper does establish is a set of facts that a causal study would have to explain: the magnitude, the cross-country uniqueness, the long-end concentration, the post-result weighting, and the lead–lag relationship between the prediction market and the bond market. The last of these is the most promising avenue for further work. A cross-country panel of elections with prediction-market coverage would allow the lead–lag pattern to be tested rather than described, and would supply the treatment variation that a single case cannot.

---

## Appendix: data sources

| Series | Source | Frequency | Coverage |
|---|---|---|---|
| 10Y yields, 8 countries | Investing.com historical data API | Daily | 2025-06 to 2026-11 |
| 10Y yields, 5 countries | Same | Daily | 2022-01 to 2026-11 |
| 5Y yield, Hungary | Same | Daily | 2025-06 to 2026-11 |
| Orbán next-PM contract | Polymarket CLOB prices-history | Daily prints | 2025-07 to 2026-05 |
| US 10Y, VIX, Brent, EUR/USD, USD/HUF | Yahoo Finance chart API | Daily | 2022-01 to 2026-11 |

All series are freely available without registration. Replication code is in `final_analysis.py`; raw responses are archived in `raw/`; intermediate output is in `out/final_results.txt`.

---
