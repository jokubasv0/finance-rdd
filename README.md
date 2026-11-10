# Shareholder Proposal Resubmission Thresholds: An RDD

Empirical finance project testing whether SEC Rule 14a-8(i)(12) resubmission
thresholds affect corporate behaviour, using a regression discontinuity design
around the **15%** vote-share cutoff.

## The design in one paragraph

Rule 14a-8(i)(12) lets a company exclude a shareholder proposal that has already
been voted on twice if, at its most recent vote, it failed to clear a threshold
that depends on how many times it has appeared. For a proposal on its **second**
appearance the bar is **15%** of votes cast. A proposal at 14.9% may be excluded
from the third ballot; one at 15.1% may not. That makes the vote share the
running variable and "did the proponent refile next year" (`refiled_t1`) the
outcome.

Thresholds are strict: 14.99% is excludable, 15.00% is not. Votes cast are
computed from raw For/Against counts, excluding abstentions and broker non-votes
per SEC Staff Legal Bulletin No. 14 — never from the rounded percentages printed
in the filing.

## Stages

| File | Purpose |
|---|---|
| `01_scrape_edgar.py` | Scrape EDGAR 8-K Item 5.07 vote tables, build the sample |
| `02_rdd_analysis.R` / `.py` | McCrary density test, local linear RD, robustness |
| `03_paper_draft.md` | Paper outline, identification, result tables |

## Reproducing

```bash
# environment
uv venv --python 3.13 .venv
. .venv/bin/activate
uv pip install requests beautifulsoup4 pandas numpy lxml rdrobust rddensity

# sanity check the parser without touching the network
python 01_scrape_edgar.py --self-test

# scrape (SEC requires a real contact address in the User-Agent)
export SEC_USER_AGENT="Your Name you@example.com"
./run_overnight.sh

# analysis
python 02_rdd_analysis.py
```

## Data

`rdd_data.csv` — 2,294 observations from 2,905 EDGAR 8-K filings, all
`data_source = EDGAR`. 323 observations form the 15%-bar RD sample.

Sample window is **2022-01-01 to 2025-12-31**. This matters: the 5%/15%/25%
thresholds only govern meetings on or after 2022-01-01. Before that the bars were
3%/6%/10%, so earlier filings cannot be scored against the 15% cutoff. Discovery
still reaches back to ~2016 because the 5-year look-back (`vote_number_5y`) and
the t+1 outcome (`refiled_t1`) both need history.

### Columns

| Column | Meaning |
|---|---|
| `vote_share` | Votes For / (For + Against), from raw counts |
| `vote_number_5y` | How many times this proposal appeared in the prior 5 years |
| `applicable_threshold` | Legal bar for this appearance (0.05 / 0.15 / 0.25) |
| `run_var` | `vote_share - applicable_threshold` — the running variable |
| `below_threshold` | Strict `<`: company *may* exclude the next submission |
| `in_15pct_sample` | `vote_number_5y == 2`, i.e. the 15% discontinuity |
| `refiled_t1` | Proponent resubmitted the same topic the following year |
| `log_assets`, `leverage`, `roa` | Covariates from SEC XBRL companyfacts |

## Known limitations

- **Small sample.** 28 observations within ±2pp of the cutoff. Estimates are
  suggestive, not precise. Reported with bias-corrected CIs and a full bandwidth
  sensitivity grid rather than a single preferred specification.
- **Imperfect take-up.** Falling below 15% *permits* exclusion; it does not
  compel it. The RD is an intent-to-treat estimate, attenuated by companies that
  decline to exclude.
- **Fuzzy topic matching.** `refiled_t1` links proposals by Jaccard similarity of
  title tokens (threshold 0.5), so it will both miss genuine refilings and
  occasionally match unrelated ones.
- **No 2026 votes.** Discovery runs into 2026 but the analysis window stops at
  2025-12-31 to keep the t+1 outcome observable.

## Attribution

Data from SEC EDGAR. Requests are rate-limited to 9/second with a descriptive
`User-Agent`, per SEC's automated-access policy. EDGAR data is public domain;
the derived dataset here is released for replication.
