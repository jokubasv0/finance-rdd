# Pricing Regime Change — data and first results

Everything below is reproducible from this folder.

```
build.py     -> out/panel_daily.csv   (merged daily panel)
analyze.py   -> out/results.txt + 3 figures
raw/         -> untouched downloads
```

Environment: `uv venv .venv` + numpy/pandas/statsmodels/matplotlib.

---

## 1. What was downloaded

| Series | Source | Coverage | Notes |
|---|---|---|---|
| P(Orbán not next PM) | Polymarket CLOB API | 2025-07-25 → 2026-05-09 | 257 daily prints |
| P(Magyar next PM) | Polymarket | same | 265 prints |
| TISZA most seats | Polymarket | 2025-12-17 → 2026-04-09 | 97 prints, dies before the vote |
| HU 10Y, 5Y | Investing.com API | daily, 2022→2026 | instrument 23932 / 23931 |
| CZ, DE, PL, RO, SI, HR, AT 10Y | Investing.com API | daily | 29241, 23693, 23947, 23990, 29335, 24002, 23862 |
| US 10Y, VIX, Brent, USDHUF | Yahoo Finance chart API | daily, 2022→2026 | `^TNX`, `^VIX`, `BZ=F`, `USDHUF=X` |

FRED's CSV endpoint refused to complete from this machine (HTTP/2 stream error), so
US 10Y / VIX / Brent come from Yahoo instead. Same underlying series.

Not obtained: Hungarian 2Y yield (no Investing.com page), CDS, BUX index
(`^BUX` not on Yahoo), foreign ownership, polls.

---

## 2. Headline facts

Window = life of the Polymarket contract, 2025-07-25 → 2026-05-08.

| | start | end | change |
|---|---:|---:|---:|
| P(Orbán does not remain PM) | 0.385 | 1.000 | +61.5 pp |
| HU 10Y | 7.13% | 5.75% | −138 bp |
| HU 5Y | 6.55% | 5.64% | −91 bp |
| CZ 10Y | 4.32% | 4.79% | +47 bp |
| **HU − CZ spread** | **2.81 pp** | **0.96 pp** | **−185 bp** |
| USDHUF | 342.5 | 302.9 | −10.1% (HUF appreciates) |

Extending to 2026-11-13: HU−CZ 2.79 → 0.30 (−249 bp), HU−DE 4.40 → 2.15 (−225 bp),
CZ−DE +24 bp, PL−DE +16 bp, RO−DE −81 bp.

### Timing decomposition

| Window | HU−CZ | HU 10Y | ΔP |
|---|---:|---:|---:|
| Jul-25 → Feb-26 | −69 bp | −66 bp | +25 pp |
| poll shift → vote (27 Feb → 9 Apr) | −18 bp | +26 bp | +5 pp |
| **full pre-election** | **−86 bp** | **−40 bp** | **+30 pp** |
| vote → end-April | −72 bp | −63 bp | +31 pp |
| vote → inauguration | −99 bp | −98 bp | +31.5 pp |
| inauguration → Nov-26 | −66 bp | — | P = 1 |

### The one result that looks robust: a stable slope across disjoint windows

bp of HU−CZ spread per 100 pp of P:

- Jul-25 → Feb-26: **−275**
- poll shift → vote: **−354**
- vote → inauguration: **−314**

Three disjoint periods, no shared observations, same magnitude. That is the
paper's best descriptive evidence of a dose–response.

### Term structure (mechanism)

HU 10Y − 5Y slope: +58 bp → +5 bp before the vote (−53 bp).
Pre-election, 10Y fell 40 bp while 5Y *rose* 13 bp.
Long end falls, short end does not → **term premium compression, not rate cuts.**
Post-election the move is parallel (slope +6 bp), which is what a level shift in
perceived sovereign risk looks like.

### Market model

Estimated on 2022-01-04 → 2025-06-30 (N = 841):
ΔHU10Y = 0.290·ΔDE (t 2.80) + 0.325·ΔUS (t 3.54) + 0.003·ΔVIX + 0.186·ΔlnBrent, R² = 0.076.

Cumulative Hungary-specific residual: −68 bp by 27 Feb, −71 bp by 9 Apr,
−142 bp by 30 Apr, −174 bp by 8 May.
So ~40% of the Hungary-specific move precedes the vote.

---

## 3. What fails

### 3.1 Daily dose–response is not identified

β on ΔP in the daily spread regression:

| spec | β | t | N |
|---|---:|---:|---:|
| M1 no controls | +0.072 | +1.25 | 193 |
| M2 + global controls | +0.027 | +0.43 | 185 |
| M3 outcome = HU10Y | −0.032 | −0.49 | 185 |
| M4 pre-election only | −0.051 | −0.47 | 166 |
| M5 post-election only | +0.372 | +3.93 | 19 |
| M6 Polymarket update days only | −0.015 | −0.21 | 130 |

No significantly negative coefficient anywhere. M5 is significant with the *wrong*
sign and N = 19, so it is noise.

Reason: the Polymarket series is stale. 138 of 193 days have a non-zero ΔP, but
the largest move is +30.9 pp on **2026-04-22**, ten days after the election and
after the spread had already fallen. There are **no prints at all between 9 and
22 April** — the market stopped trading once the result was obvious.

### 3.2 Weekly and monthly

- Weekly: β = +0.189 (t = 0.63), N = 41. Nothing.
- Monthly: β = −2.687 (t = −8.16), N = 10, R² = 0.62.
  Leave-one-out: dropping April 2026 gives β = −0.505 (t = −1.02, p = 0.31).
  The monthly result is one observation.

### 3.3 Placebo countries

Spread vs Germany on ΔP, same controls:

| | HU | CZ | PL | RO | SI | HR | AT |
|---|---:|---:|---:|---:|---:|---:|---:|
| β | −0.032 | −0.059 | −0.120 | +0.156 | +0.015 | +0.025 | −0.010 |
| t | −0.49 | −1.29 | −0.63 | +1.62 | +0.20 | +1.14 | −0.27 |

Hungary is not distinguishable from any donor. Good news for the placebo test,
bad news for the daily design: ΔP carries no Hungarian-specific information at
daily frequency.

### 3.4 Continuous DiD

Country + date fixed effects, 7 countries, N = 1350:
β(P × HU) = −2.694 pp per unit P = **−269 bp per 100 pp**, conventional se 0.126.

Randomisation inference (re-label each country as treated):
HU −2.694, CZ +0.665, PL +0.638, RO +0.031, SI +0.744, HR +0.306, AT +0.312.
HU is rank 1 of 7 → **RI p = 0.14**. Cannot reject at 5% with seven donors.

### 3.5 The control is contaminated

Over the full window CZ−DE widened +24 bp and PL−DE +16 bp. Czech and Polish
yields rose for their own reasons, so part of the HU−CZ compression is not
Hungarian improvement. HU−DE (−225 bp) is the cleaner number, and it is 24 bp
smaller than HU−CZ.

### 3.6 A quarter of the move happens after P = 1

Inauguration → Nov 2026: another −66 bp of HU−CZ compression with the contract
already resolved at 1.0. Regime-change probability cannot explain that. Either
there is a persistent trend (rating upgrades, EU funds, fiscal), or the spread
was still mean-reverting.

---

## 4. Verdict

The Polymarket contract is a good *narrative* variable and a bad *treatment*
variable at daily frequency.

What the data supports:

> Between July 2025 and May 2026 the HU−CZ spread fell 185 bp while the
> market-implied probability of regime change rose from 0.39 to 1.00. Across
> three disjoint sub-periods the implied slope is stable at −275 to −354 bp per
> 100 pp. The compression is concentrated at the long end and coincides with a
> 10% HUF appreciation.

What it does not support:

> A daily or weekly causal effect of ΔP on Δspread. The prediction market is
> stale, the entire estimate rests on April 2026, and randomisation inference
> with seven donors gives p = 0.14.

So the paper should use Polymarket for **framing, descriptives and the
dose–response consistency check**, and use the **event study / market model** for
identification. Or replace P with a poll-based probability series that has real
continuous variation (see below).

---

## 5. What you need to pull by hand

Ranked by how much it improves the paper.

1. **Hungarian 2Y (or 1Y) benchmark yield, daily.**
   Source: MNB `statisztika.mnb.hu/timeseries/data-10130` or ÁKK benchmark yields.
   Why: the 10Y−5Y slope already suggests term premium, but 2Y vs 10Y is the
   textbook test. Without it a referee says "MNB cuts".
   Cost: 10 minutes, download CSV, drop in `raw/`.

2. **Opinion polls, 2025–2026.**
   Source: Wikipedia "Opinion polling for the 2026 Hungarian parliamentary
   election" (table of party shares by pollster and date), or PolitPro.
   Why: gives a *poll-based* probability of regime change with genuine
   continuous variation, and lets you instrument Polymarket with polls.
   Cost: 30–60 minutes of copy-paste.

3. **MNB rate decision dates, 2025–2026.**
   Source: MNB press releases.
   Why: event dummies / exclusion windows for the main confounder.
   Cost: 10 minutes.

4. **Hungary rating actions and EU-funds milestones.**
   Source: Moody's/S&P/Fitch press releases; European Commission MFF/conditionality
   news.
   Why: dates to exclude or control for.
   Cost: 20 minutes.

5. **Foreign ownership share of Hungarian government bonds.**
   Source: ÁKK quarterly statistics.
   Why: the demand-channel mechanism.
   Cost: 15 minutes, quarterly so only ~6 points.

6. **CDS spread, 5Y Hungary.** Optional, usually paywalled. Skip unless free.

7. **BUX index.** `^BUX` is not on Yahoo. Try Investing.com or BSE directly.
   Optional corroboration.

---

## 6. Decision you need to make

**Option A — Polymarket as framing, event study as identification.**
Keep the brief's DiD and market model. Use Polymarket for Figure 1 and the
three-window slope. Honest, quick, no new data. Weakest point: the treatment is
descriptive, not causal.

**Option B — Poll-based probability as the treatment.**
Build P from polls, use Polymarket as a validation/robustness series. Real
continuous variation, real dose–response, and an actual instrument. Needs item 2
above. Strongest paper, ~1 week more work.

**Option C — Cross-country panel.**
Elections in CEE 2010–2026, monthly yields, event study + synthetic control.
Publishable but far beyond a 10-minute assignment.

Recommendation: **A now, B if the polls turn out clean.** C is a different paper.

---

## 7. Files

- `out/panel_daily.csv` — merged panel, one row per calendar day
- `out/results.txt` — full regression output as printed
- `out/fig1_prob_vs_spread.png` — spread vs P, three event markers
- `out/fig2_monthly_scatter.png` — monthly ΔP vs Δspread, April labelled
- `out/fig3_market_model.png` — cumulative Hungary-specific residual
