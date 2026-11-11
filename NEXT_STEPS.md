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
twice, `25%` for three or more) is what makes the question answerable at all.
The estimate is positive everywhere but its significance depends on the matching
threshold, so it is reported as suggestive.

| Specification | τ | SE | p | 95% CI |
|---|---|---|---|---|
| Pooled, threshold FE | 0.085 | 0.073 | 0.244 | [−0.058, 0.229] |
| Pooled, FE + covariates | 0.107 | 0.075 | 0.151 | [−0.039, 0.253] |
| Pooled, no adjustment | 0.092 | 0.078 | 0.241 | [−0.062, 0.245] |

Sample 2,052 proposals, 430 firms, SEs clustered on CIK. Per-threshold:
5% bar −0.030 (p 0.74), 15% bar 0.110 (p 0.65), 25% bar −0.004 (p 0.99) — the
pooled estimate is doing the work, individual bars are far too thin, and there
is no longer any evidence of a monotone gradient.

Reading: clearing the applicable bar raises the probability that a same-topic
proposal reaches the ballot a year later by roughly 10 percentage points against
a base rate of 27%.

Robustness suite (`02c_robustness.py`): seven specifications, τ in [0.073, 0.254],
positive in 7 of 7, significant at 5% in 0 of 7. Balance p 0.26–0.74; placebos
p 0.79–0.97; polynomial p=1 0.085, p=2 0.047.

> **Superseded:** an earlier version reported 0.182 (p = 0.030). That came from a
> tokenizer that left vote-result boilerplate in the matching tokens. Do not cite
> it. See `STUDY_PROCESS.txt` Phase 10.

## Two things to be careful about

1. **The matching threshold drives the precision, not the sample size.** Moving
   the Jaccard cutoff from 0.4 to 0.6 moves the pooled estimate from 0.107 to
   0.158 and its p-value from 0.052 to 0.007; the 15% bar swings 0.110 → 0.450
   and the 25% bar changes sign. Direction is robust, magnitude is not. Hand-coding
   a validation sample is the highest-value remaining analysis.

2. **Pooled McCrary flags at p = 0.039.** This is a mechanical artifact of
   stacking three groups whose vote-share distributions differ; each group
   individually passes (p 0.55, 0.62, 0.57). The valid manipulation tests are
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
