# Pricing Regime Change: Hungary's 2026 Election and Sovereign Risk

Did markets price the fall of a government before it fell?

Hungary's April 2026 election ended sixteen years of Fidesz rule. This project studies the
daily behaviour of Hungarian sovereign yields against six Central European peers, and compares
the repricing with a Polymarket contract on whether Viktor Orbán would remain prime minister.

## Headline numbers

| | |
|---|---|
| HU 10Y yield, 25 Jul 2025 → 8 May 2026 | 7.13% → 5.75% (**−138 bp**) |
| HU 10Y minus six-peer average | 2.74 → 1.16 pp (**−157 bp**) |
| DiD vs seven neighbours, country trends | **−129 bp** (DK t = −7.9) |
| DiD, no trends | −177 bp |
| Randomisation inference, 8 units | p = 0.125 (floor of 1/8) |
| Share of compression before the vote | 35% (−56 bp), 65% after the result |
| Countries in the sample whose yield fell | 1 of 8 (Hungary) |
| Placebo-date p-value | 0.15 |
| 9 Apr 2026 (3 days before vote): Polymarket vs bond-implied | 69% vs 35% |

## What the paper claims

A conditional estimate, not an identified treatment effect.

The identification is a two-way fixed-effects difference-in-differences against the seven other
countries, with country and calendar-date fixed effects and country-specific linear trends. It
gives −129 bp. The event study is reported in full: the pre-treatment leads are not flat, a joint
test rejects them, and the trend specification exists because of that. With one treated unit,
randomisation inference cannot go below p = 0.125, and the paper says so where the estimate is
reported.

The daily design — spread changes on changes in the Polymarket probability — returns β ≈ 0 and
is reported as a null, because the probability series has only two moves above 10 bp of
substance: opening-week liquidity discovery, and a print ten days after the result.

## Layout

```
final_analysis.py     descriptive results and figures; writes out/final_results.txt
did_analysis.py       difference-in-differences, event study, placebos; writes out/did_results.txt
build_docx.py         renders out/paper.md to out/Pricing_Regime_Change.docx
raw/                  archived API responses (Investing.com, Yahoo Finance, Polymarket)
out/                  paper.md, talk.md, figures, results, panel
```

## Reproduce

```bash
python3 -m venv .venv
uv pip install --python .venv/bin/python numpy pandas statsmodels matplotlib scipy python-docx linearmodels
.venv/bin/python final_analysis.py     # descriptive numbers + six figures
.venv/bin/python did_analysis.py       # DiD, event study, placebos + two figures
.venv/bin/python build_docx.py         # paper docx
```

## Data

All series are freely available without registration.

- **Sovereign yields** — Investing.com historical data API, eight countries, daily
- **Polymarket** — CLOB `prices-history` endpoint for the Orbán next-PM contract
- **US 10Y, VIX, Brent, EUR/USD, USD/HUF** — Yahoo Finance chart API

`raw/` contains the exact responses used, so results reproduce without refetching.

## Known gaps

Daily Hungarian 2-year and Slovak 10-year yields were not obtainable from this source.
The 2-year would let the term-structure test separate rate expectations from term premium
directly instead of leaning on the 10Y−5Y slope.
