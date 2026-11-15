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
| DiD vs neighbours, 2024–2026, kinked trend | **−109 bp** (DK t = −11.3) |
| DiD, no trend / linear trend | −104 / −109 bp |
| DiD through November 2026 | −172 bp |
| Randomisation inference, 8 units | p = 0.125 (floor of 1/8) |
| Share of compression before the vote | 35% (−56 bp), 65% after the result |
| Countries whose yield fell more than 21 bp | 1 of 8 (Hungary); Romania −21 bp |
| Placebo treatment dates, panel truncated before the event | −0.31 to +0.18 pp, none near −1.09 |
| Random-window placebo | withdrawn as invalid (trending series) |
| 9 Apr 2026 (3 days before vote): Polymarket vs bond-implied | 69% vs 35% |

## What the paper claims

A conditional estimate, not an identified treatment effect.

The identification is a two-way fixed-effects difference-in-differences against neighbouring
markets on a 2024–2026 panel, with country and calendar-date fixed effects and a country trend
fitted before the treatment date and held flat afterwards. It gives −109 bp, and the three possible
trend treatments span five basis points on that sample.

The sample starts in 2024 because of a placebo-date test, not a preference: on 2022 data the
no-trends design returns −1.1 at almost every fake election date, because the 2022 energy-crisis
convergence runs through every window. Truncating the panel before the real event and re-running at
fake dates gives ≈0 throughout on 2024 data. The event study is reported in full: the pre-treatment
leads oscillate without trending, but a joint test rejects that they are all zero. With one treated
unit, randomisation inference cannot go below p = 0.125, and the paper says so where the estimate is
reported.

The daily design — spread changes on changes in the Polymarket probability — returns β ≈ 0 and
is reported as a null, because the probability series has only two moves above 10 percentage points
of substance: opening-week liquidity discovery, and a print ten days after the result.

## Layout

```
build.py              merges raw/ into out/panel_daily.csv
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
.venv/bin/python build.py              # merged daily panel -> out/panel_daily.csv
.venv/bin/python final_analysis.py     # descriptive numbers + figures
.venv/bin/python did_analysis.py       # DiD, event study, placebos + two figures
.venv/bin/python build_docx.py         # paper docx
```

## Data

All series are freely available without registration.

- **Sovereign yields** — Investing.com historical data API, eight countries, daily
- **Polymarket** — CLOB `prices-history` endpoint for the Orbán next-PM contract
- **US 10Y, VIX, Brent, EUR/USD, USD/HUF** — Yahoo Finance chart API

`raw/` contains the exact responses used, so the pipeline reproduces without refetching. It is
a **frozen snapshot**: there is no fetch script in this repository. The endpoints are undocumented
and the Polymarket contract has since resolved, so a fetch step would not be reproducible even if
one were shipped. `build.py` reads only the archived JSON, and `out/panel_daily.csv` is its output.

## Known gaps

Daily Hungarian 2-year and Slovak 10-year yields were not obtainable from this source.
The 2-year would let the term-structure test separate rate expectations from term premium
directly instead of leaning on the 10Y−5Y slope.
