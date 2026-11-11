# Handoff — resume here

## Status

| Stage | Status |
|---|---|
| 1. EDGAR scrape | ✅ `rdd_data.csv`, 2,294 obs, 100% real EDGAR data |
| 2. Single-cutoff RD (15%) | ✅ `02_rdd_analysis.py` — underpowered, null |
| 2b. Multi-cutoff RD (pooled) | ✅ `02b_multi_cutoff_rd.py` — **significant** |
| 3. Paper draft | ⬜ next |
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

- **Stage 3 paper draft** — not started. Use the pooled FE + covariates spec as
  the headline, per-threshold as heterogeneity, and the single-cutoff 15% run as
  the motivating "this alone cannot answer the question" discussion.
- **First stage** (optional, needs a new scrape): measure whether the proposal
  was actually excluded, via SEC no-action letters, instead of the noisy
  `refiled_t1` proxy.
- **Label noise.** 75th percentile of `vote_share` is 0.94 vs a 0.31 median;
  some near-unanimous rows may be management proposals misclassified as
  shareholder proposals. Matters for the 5% bar, which those rows dominate.
- **Fuzzy refiling.** `refiled_t1` links on Jaccard similarity of title tokens
  (0.5). Largest single source of measurement error in the outcome.
- **Unverified claim** in the Stage 1 docstring: that the SEC proposed
  rescinding Rule 14a-8 in September 2026. Verify or delete.
- **R not installed.** Stage 2 runs on the authors' official Python ports
  (`rdrobust 2.1.1`, `rddensity 3.0`). `02_rdd_analysis.R` is still owed as the
  spec's deliverable and needs R + gfortran (sudo or `pkexec`).

## Commands

```bash
cd ~/rdd-paper
. .venv/bin/activate
python 02_rdd_analysis.py        # single-cutoff (15%) analysis
python 02b_multi_cutoff_rd.py    # pooled multi-cutoff analysis
python 01_scrape_edgar.py --self-test
```
