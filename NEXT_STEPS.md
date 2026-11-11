# Handoff — resume here

## Status

| Stage | Status |
|---|---|
| 1. EDGAR scrape | ✅ `rdd_data.csv`, 2,294 obs, 100% real EDGAR data |
| 2. Single-cutoff RD (15%) | ✅ `02_rdd_analysis.py` / `.R` — underpowered, null |
| 2b. Multi-cutoff RD (pooled) | ✅ `02b_multi_cutoff_rd.py` / `.R` — **significant** |
| 3. Paper draft | ✅ `03_paper_draft.md` — full draft, real numbers |
| GitHub | ✅ pushed to `jokubasv0/finance-rdd` (private, SSH remote) |

## Headline result

Pooling all three 14a-8(i)(12) bars (`5%` for a proposal voted once, `15%` for
twice, `25%` for three or more) turns an uninformative design into a real one.

| Specification | τ | SE | p | 95% CI |
|---|---|---|---|---|
| Pooled, threshold FE | 0.158 | 0.081 | 0.052 | [−0.001, 0.318] |
| **Pooled, FE + covariates** | **0.182** | **0.084** | **0.030** | **[0.017, 0.346]** |
| Pooled, no adjustment | 0.148 | 0.088 | 0.092 | [−0.024, 0.321] |

Sample 2,077 proposals, 431 firms, SEs clustered on CIK. Per-threshold:
5% bar 0.030 (p 0.74), 15% bar 0.166 (p 0.56), 25% bar 0.208 (p 0.34) — the
pooled estimate is doing the work, individual bars are too thin.

Reading: clearing the applicable bar raises the probability the proponent
resubmits by roughly 18 percentage points against a base refiling rate of 27%.

Robustness all passes: bandwidth grid τ 0.11–0.14 with p 0.027–0.215 and a
stable sign; covariate balance p 0.30–0.85; placebo cutoffs p 0.82; polynomial
p=1 0.158 and p=2 0.172.

## Two things to be careful about

1. **Pooled McCrary flags at p = 0.055.** This is a mechanical artifact of
   stacking three groups whose vote-share distributions differ; each group
   individually passes (p 0.53, 0.41, 0.81). The valid manipulation tests are
   the per-threshold ones. Do not report the pooled test as evidence of sorting.
2. **Pooling assumes a comparable effect across bars.** Threshold FE absorb
   level differences but not slope differences. The per-threshold spread
   (0.03 → 0.17 → 0.21) is consistent with a stronger effect at higher bars,
   which pooling understates. Report both, and frame the pooled estimate as the
   average across bars.

## Still open

- **Stage 3 paper draft** — first full draft written (`03_paper_draft.md`), with
  abstract, institutional framework, identification, all result tables and
  threats to validity. Remaining work is editorial: tighten the prose, verify
  every citation, and decide whether the per-threshold heterogeneity (Section
  5.4) is a finding or a caveat.
- **First stage** (optional, needs a new scrape): measure whether the proposal
  was actually excluded, via SEC no-action letters, instead of the noisy
  `refiled_t1` proxy.
- **Label noise.** 75th percentile of `vote_share` is 0.94 vs a 0.31 median;
  some near-unanimous rows may be management proposals misclassified as
  shareholder proposals. Matters for the 5% bar, which those rows dominate.
- **Fuzzy refiling.** `refiled_t1` links on Jaccard similarity of title tokens
  (0.5). Largest single source of measurement error in the outcome.
- **Unverified claim** in the Stage 1 docstring: that the SEC proposed
  rescinding Rule 14a-8 in September 2026. Verify or delete. The paper now
  states this conditionally and carries a `TODO(jn)` marker.
- **Rule text now verified** against 17 CFR 240.14a-8 (eCFR). Section 2 was
  rewritten from the primary source and now covers: proponent eligibility
  ($2k/3yr, $15k/2yr, $25k/1yr; one proposal per meeting; 500 words; 120-day
  deadline; two-year ban for non-attendance), all thirteen exclusion grounds,
  the Rule 14a-8(j) no-action procedure (80-day filing, burden on company),
  and an explicit subsection on why clearing a threshold does not guarantee a
  ballot. Two corrections against earlier notes: ground (i)(5) is an economic
  relevance test, not a social-policy test, and (i)(6) is absence of power.
- **Three-year recency clause** in (i)(12) is non-binding in our design (the
  most recent vote is always the current one, which is within 18 months of the
  outcome), but the five-year window is measured from the vote date rather than
  the company's evaluation date — documented in Section 6 as a small
  approximation.
- ~~**R not installed.**~~ **Resolved.** R 4.6.2 installed to `~/.local/bin`
  via `rig add release --user`. `rdrobust` and `rddensity` installed into
  `~/R/library` (they compile without gfortran — the current CRAN versions are
  C++, not Fortran). Both R scripts run and reproduce the Python output to the
  last digit. Run them with `R_LIBS_USER=~/R/library Rscript <script>.R`.
## Commands

```bash
cd ~/rdd-paper
. .venv/bin/activate
python 02_rdd_analysis.py        # single-cutoff (15%) analysis
python 02b_multi_cutoff_rd.py    # pooled multi-cutoff analysis
python 01_scrape_edgar.py --self-test

# same analyses in R (reproduces the Python output exactly)
export R_LIBS_USER=~/R/library
Rscript 02_rdd_analysis.R
Rscript 02b_multi_cutoff_rd.R
```
