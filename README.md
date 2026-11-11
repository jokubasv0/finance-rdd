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
| `02_rdd_analysis.py` | Single-cutoff RD at 15% (the spec's baseline) |
| `02b_multi_cutoff_rd.py` | Pooled RD across all three bars — the main result |
| `02c_robustness.py` | Year FE, topic FE, sample-variant robustness suite |
| `02_rdd_analysis.R` | R equivalent of the 15% spec |
| `02b_multi_cutoff_rd.R` | R equivalent of the pooled spec |
| `03_paper_draft.md` | Full paper draft |
| `STUDY_PROCESS.txt` | Chronological audit trail: every step, bug and assumption |

## Headline result

Pooling all three resubmission bars (5%, 15%, 25%) turns an underpowered
single-cutoff design into one that can answer the question. The estimate is
positive in every specification tried, but its significance depends on how
aggressively proposals are matched across years, so it is reported as suggestive:

| Specification | τ | SE | p | 95% CI |
|---|---|---|---|---|
| Pooled, threshold FE | 0.085 | 0.073 | 0.244 | [−0.058, 0.229] |
| Pooled, FE + covariates | 0.107 | 0.075 | 0.151 | [−0.039, 0.253] |
| Pooled, no adjustment | 0.092 | 0.078 | 0.241 | [−0.062, 0.245] |

2,052 proposals, 430 firms, SEs clustered on CIK. Clearing the applicable bar
raises the probability that a same-topic proposal reaches the ballot a year later
by roughly 10pp against a base rate of 27%. The 15% cutoff alone is far too thin
to detect this (29 observations within ±2pp, minimum detectable effect ≈ 76pp).

**Read the sensitivity table before quoting any number.** Moving the Jaccard
matching threshold from 0.4 to 0.6 moves the pooled estimate between 0.107 and
0.158 and its p-value between 0.052 and 0.007. Direction is robust; magnitude and
significance are not. See Section 5.8 of the paper and `STUDY_PROCESS.txt`.

> The earlier figure of 0.182 (p = 0.030) came from a tokenizer that left
> vote-result boilerplate in the topic-matching tokens. It is superseded and must
> not be cited.

## Reproducing

```bash
# environment (Python)
uv venv --python 3.13 .venv
. .venv/bin/activate
uv pip install requests beautifulsoup4 pandas numpy lxml rdrobust rddensity

# sanity check the parser without touching the network
python 01_scrape_edgar.py --self-test

# scrape (SEC requires a real contact address in the User-Agent)
export SEC_USER_AGENT="Your Name you@example.com"
./run_overnight.sh

# analysis (Python)
python 02_rdd_analysis.py        # single-cutoff, 15%
python 02b_multi_cutoff_rd.py    # pooled, main result

# analysis (R) -- reproduces the Python output exactly
Rscript -e 'install.packages(c("rdrobust","rddensity"))'
Rscript 02_rdd_analysis.R
Rscript 02b_multi_cutoff_rd.R
```

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
| `refiled_t1` | Same-topic proposal reached the ballot the following year |
| `log_assets`, `leverage`, `roa` | Covariates from SEC XBRL companyfacts |

## Known limitations

- **Small sample at any single cutoff.** Only 29 observations sit within ±2pp of
  the 15% bar, giving a minimum detectable effect near 76pp. This is why the
  headline estimate pools all three bars; see the next point for the cost.
- **Matching threshold drives the precision.** The topic linkage that assigns
  each proposal to a bar is a Jaccard match on title tokens. Moving the cutoff
  from 0.4 to 0.6 moves the pooled estimate from 0.107 to 0.158 and its p-value
  from 0.052 to 0.007. Direction survives; magnitude and significance do not.
  This is the binding limitation, and more data does not fix it.
- **Pooling assumes comparable effects.** Stacking the 5%, 15% and 25% bars
  assumes the effect of becoming excludable is similar across them. Threshold
  fixed effects absorb level differences but not slope differences. Per-bar
  estimates are too imprecise to establish heterogeneity either way.
- **Pooled density test is not meaningful.** The pooled McCrary statistic
  (p = 0.039) reflects the three groups' differing vote-share distributions, not
  manipulation. Each threshold passes individually (p = 0.55, 0.62, 0.57); those
  are the valid tests.
- **Imperfect take-up.** Falling below the bar *permits* exclusion; it does not
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
