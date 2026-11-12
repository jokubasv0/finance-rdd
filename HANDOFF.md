# HANDOFF — read this before touching anything

Last updated: 2026-11-12
Repo: `git@github.com:jokubasv0/finance-rdd.git` (private)
Working dir: `~/rdd-paper`

---

## 0. The one thing you must know

**`03_paper_draft.md` is out of date and its headline numbers are wrong.**
It still reports the pre-fix estimate of 0.107, a sample of 2,052, and a base
rate of 27%. The correct current numbers are in Section 3 of this file. Do not
quote anything from the paper until Stage C is finished.

The data layer was rebuilt twice. The paper has not caught up.

---

## 1. What the study is

Does SEC Rule 14a-8(i)(12) deter shareholder proponents from resubmitting a
failed proposal? The rule sets a bar based on how many times a proposal has been
voted on in the preceding five calendar years:

| previous votes | bar |
|---|---|
| 1 | 5% |
| 2 | 15% |
| 3 or more | 25% |

Below the bar the company may exclude the next submission; above it, it may not
exclude on this ground. The design is a regression discontinuity on
`vote_share - applicable_bar`, pooled across the three bars.

The 5/15/25 schedule governs meetings on or after 2022-01-01. Before that the
bars were 3/6/10. The analysis window is 2022-01-01 .. 2025-12-31.

**Estimand, stated precisely:** the reduced-form effect of *eligibility* for
exclusion on the probability that a proposal on the same subject **reaches a
ballot** at the next annual meeting. It is not an estimate of filing behaviour,
and it is not a LATE, because exclusion is never observed.

---

## 2. What has been done

### Stage A — data fixes (COMPLETE)

Two serious bugs were found and fixed. Both were in the original scraper.

1. **Director-election contamination.** The parser enriched short descriptions
   with surrounding paragraph text, so a director nominee row (`John H Tyson`)
   inherited a neighbouring sentence containing "one shareholder proposal" and
   was classified as a shareholder proposal — carrying the *director's* ~97%
   approval as its vote share. 681 contaminated rows were removed.
   Fix: `_is_person_name()` + `_PERSON_NAME_RE` + `_NON_NAME_WORDS` in
   `01_scrape_edgar.py`; a bare personal name is left alone so `SP_RE` fails.

2. **`vote_number_5y` counted rows, not meetings.** The linkage summed one
   increment per matching row. A single meeting can yield many similar rows, so
   proposals were pushed into the 25% bar on one meeting's evidence. The maximum
   value was 65, which decomposes as 37 rows across 3 meetings.
   Fix: `add_resubmission_variables` now counts **distinct meeting dates** via a
   `matched_dates` set.

`history_complete` was also made meaningful: it now requires the firm's first
observed filing to precede the start of the look-back window, rather than merely
comparing the analysis start date.

### Analysis changes (COMPLETE)

- `MDE_Z = 2.802` and an `mde()` helper added to both `02_rdd_analysis.py` and
  `02b_multi_cutoff_rd.py`; every table now carries an MDE column.
- `02b_multi_cutoff_rd.py` now computes the **inverse-variance weighted average**
  of the per-bar jumps, so the pooled estimate can be read against it.

### Not done

- Stage B (inference reporting) — partially applied via MDE, rest pending.
- Stage C (text sweep) — not started. Paper is stale.
- R scripts have **not** been re-run on the rebuilt data. They will not match.

---

## 3. The authoritative numbers

Data: `rdd_data.csv`, 1,818 valid proposal observations.
Pooled RD sample after dropping right-censored outcomes: **1,603 proposals,
427 firms**, 153 within ±2pp of their own bar.

### Sample by bar

| bar | n | firms | within ±2pp | refile rate |
|---|---|---|---|---|
| 5% | 1,136 | 402 | 108 | 0.173 |
| 15% | 283 | 150 | 31 | 0.258 |
| 25% | 184 | 79 | 14 | 0.478 |

### Pooled estimates (bias-corrected, clustered on CIK)

| spec | τ | SE | p | 95% CI | MDE |
|---|---|---|---|---|---|
| FE | 0.068 | 0.080 | 0.396 | [−0.089, 0.225] | 0.224 |
| **FE + covariates** | **0.078** | **0.081** | **0.337** | **[−0.081, 0.237]** | **0.228** |
| no adjustment | 0.051 | 0.083 | 0.542 | [−0.112, 0.213] | 0.232 |

### Per-bar (bias-corrected, clustered)

| bar | τ | SE | p | MDE |
|---|---|---|---|---|
| 5% | −0.028 | 0.088 | 0.752 | 0.246 |
| 15% | 0.110 | 0.231 | 0.634 | 0.647 |
| 25% | −0.019 | 0.206 | 0.925 | 0.577 |

**Inverse-variance weighted average of the per-bar jumps: −0.012 (SE 0.076).**

This is the single most important diagnostic in the project. The pooled +0.078
is **not** an average of the three per-bar jumps. It is produced by forcing one
common bandwidth and one common polynomial across bars whose running-variable
distributions differ. Any write-up that reports the pooled number without this
one next to it is misleading.

### Density tests

| sample | t | p |
|---|---|---|
| 5% bar | −0.432 | 0.666 |
| 15% bar | 0.421 | 0.674 |
| 25% bar | 0.812 | 0.417 |
| pooled | 2.378 | **0.017** |

The paper currently claims the pooled failure is a "mechanical artifact of
stacking". **That claim is mathematically false** — a mixture of densities that
are each continuous at zero is itself continuous. Either the per-bar tests are
underpowered or something real is happening. This needs diagnosis, not
dismissal.

### Robustness suite (`02c_robustness.py`, n=1,583)

| spec | τ | SE | p |
|---|---|---|---|
| 1. baseline | 0.080 | 0.081 | 0.324 |
| 2. + year FE | 0.058 | 0.078 | 0.460 |
| 3. + topic FE | 0.104 | 0.078 | 0.181 |
| 4. + year + topic FE | 0.079 | 0.075 | 0.292 |
| 5. both FE, no covariates | 0.066 | 0.074 | 0.374 |
| 6. 25% bar = 3rd submission only | 0.059 | 0.075 | 0.434 |
| 7. drop 5% bar | 0.264 | 0.151 | 0.080 |

Range [0.058, 0.264], positive in 7/7, significant at 5% in 0/7.

### Raw (non-RD) comparison — the descriptive fact

| window | below bar | above bar | gap | SE | p (clustered) |
|---|---|---|---|---|---|
| whole sample | 11.6% (n=352) | 25.3% (n=1,251) | +13.6pp | 2.1pp | <0.001 |
| ±2pp | 6.6% (n=76) | 18.2% (n=77) | +11.6pp | 5.3pp | 0.048 |
| ±5pp | 5.7% (n=247) | 19.6% (n=204) | +13.9pp | 3.2pp | 0.0006 |
| ±10pp | 6.5% (n=294) | 23.3% (n=361) | +16.8pp | 2.7pp | <0.001 |

Fine bins around the cutoff:

| bin | n | refile rate |
|---|---|---|
| (−0.03, −0.02] | 31 | 0.000 |
| (−0.02, −0.01] | 39 | 0.000 |
| (−0.01, 0] | 37 | 0.135 |
| (0, +0.01] | 41 | 0.146 |
| (+0.01, +0.02] | 36 | 0.222 |
| (+0.02, +0.03] | 49 | 0.204 |

Pooled (−0.03, 0] = 4.7% (5/107) vs (0, +0.03] = 19.0% (24/126).

### NEW FINDING — the RD is not bandwidth-stable

Manual local-linear RD, clustered on CIK:

| h | jump | SE | p |
|---|---|---|---|
| 0.020 | −0.045 | 0.111 | 0.689 |
| 0.050 | +0.118 | 0.072 | 0.104 |
| 0.075 | +0.135 | 0.067 | 0.044 |
| 0.100 | +0.129 | 0.058 | 0.027 |
| 0.150 | +0.159 | 0.054 | 0.003 |
| 0.200 | +0.185 | 0.051 | <0.001 |

The jump grows monotonically with bandwidth and is null at the narrowest window.
A genuine discontinuity should be stable. This is the strongest single argument
against the current specification and must go in the paper.

Why: the outcome rises steeply in vote share above the bar (slope ≈ +1.18 within
±10pp), so part of what looks like a jump is a gradient. At this sample size the
RD cannot separate the two.

---

## 4. What the next agent should do

### B1. Decide how to present the estimate — THIS IS A JUDGEMENT CALL

The pooled number contradicts the weighted average of the per-bar jumps. Options:

- **Per-bar only**, stating the design is underpowered at every bar.
- **Keep pooling** but always report the −0.012 weighted average beside it.

Recommendation: per-bar as primary, pooled as a secondary "pooled for power"
row with the contradiction stated explicitly. Do not let the pooled 0.078 stand
alone.

### B2. Diagnose the pooled density failure honestly

Remove the "mechanical artifact" claim. Investigate whether the jump comes from
one bar, one year, or one topic; if it cannot be explained, report it as an
unresolved threat to identification.

### B3. Add the bandwidth-instability diagnostic as its own section

The table in Section 3 above. This is new and currently exists nowhere in the
paper.

### B4. Stage C — text sweep of `03_paper_draft.md`

Replace everywhere:

| stale | correct |
|---|---|
| 0.107 | 0.078 (or per-bar, per B1) |
| 2,052 | 1,603 pooled / 1,818 total |
| 430 firms | 427 |
| 27% base rate | 0.213 (recompute on the new data) |
| 217 dropped | 242 (recompute — currently inconsistent with line 328) |
| 153 within ±2pp | 153 (this one is still right) |

Also:

- Section 2.6 keys the threshold regime off `filing_date`; the rule applies to
  the **meeting** date. An 8-K filed in January 2022 can report a December 2021
  meeting governed by 3/6/10. Either filter on a meeting date or acknowledge it.
- The five-year window is implemented as 1,827 days; the rule counts calendar
  years. Already noted in Section 6, keep.
- The two SEC claims are now **verified** and the TODO should be gone. See
  Section 6 below.

### B5. Re-run the R scripts

`02_rdd_analysis.R` and `02b_multi_cutoff_rd.R` have not been run since the data
was rebuilt. They will not match the Python output. Either re-run them or note
in the appendix that they are stale.

---

## 5. File map

```
01_scrape_edgar.py        Stage 1 scraper (patched twice; see Stage A)
02_rdd_analysis.py        Stage 2 single 15% cutoff + MDE
02b_multi_cutoff_rd.py    Stage 2b pooled + per-bar + weighted average + MDE
02c_robustness.py         Stage 2c seven-spec suite (year FE, topic FE, etc.)
02_rdd_analysis.R         R twin of 02 (STALE — not re-run)
02b_multi_cutoff_rd.R     R twin of 02b (STALE — not re-run)
03_paper_draft.md         the paper (STALE — see Section 0)
STUDY_PROCESS.txt         chronological audit trail, assumptions A1-A15
README.md                 repo guide (STALE headline)
NEXT_STEPS.md             status notes (STALE headline)
HANDOFF.md                this file

rdd_data.csv              CURRENT — 1,818 observations, Jaccard 0.5
rdd_data_t40.csv          Jaccard 0.4 variant (pre-Stage-A, stale)
rdd_data_t60.csv          Jaccard 0.6 variant (pre-Stage-A, stale)
rdd_data_v1.csv           pre-audit backup (very stale, keep for history)

results/                  all tables, regenerated on current data
edgar_cache/              1.8 GB disk cache — do not delete, re-runs depend on it
```

---

## 6. Things that are settled — do not re-litigate

- **The two SEC claims are true and verified.** (a) 17 Nov 2025: Corp Fin said
  it would not respond to 14a-8 no-action requests for the 2025–26 season except
  under (i)(1). (b) 14 Aug 2026: it discontinued responding entirely, including
  (i)(1), indefinitely, and stopped issuing "no objection" letters
  (sec.gov/newsroom/speeches-statements/corpfin-statement-rule-14a-8-process-081426).
  (c) 16 Sept 2026: SEC proposed rescission of Rule 14a-8, Release No. 34-106383,
  File S7-2026-32, 91 FR 59904, comments due 20 Nov 2026. Restore these as fact
  with citations; do not delete them.
- **`vote_share` comes from raw counts, never printed percentages.** Verified:
  zero nulls in `votes_for`/`votes_against`, no mass on any threshold.
- **The comparison is strict.** 14.99% is excludable, 15.00% is not.
- **Abstentions and broker non-votes are excluded** per SEC Staff Legal Bulletin
  No. 14. Denominator is For + Against.
- **The three-year recency clause does not bind.** The most recent vote is always
  the current one, observed 6–18 months before the outcome.
- **Rule text details** (verified against eCFR): (i)(5) is an *economic
  relevance* test, not social policy; (i)(6) is *absence of power*; eligibility
  is tiered $2k/3yr, $15k/2yr, $25k/1yr; one proposal per person per meeting;
  500-word cap; 120-day deadline; 80-day no-action filing deadline; burden of
  persuasion is on the company.

---

## 7. Traps

1. **The synthetic fallback is dangerous.** `01_scrape_edgar.py` writes 200 fake
   rows to `rdd_data.csv` if it finds fewer than `min_obs` real observations.
   Always run with `--min-obs 0` for real work. This once silently produced fake
   data overnight because the EFTS URL was wrong and returned 403.
2. **`add_resubmission_variables` runs before the date filter.** Priors from
   2017–2021 count toward `vote_number_5y` but are absent from the exported CSV.
   The CSV alone cannot reproduce the linkage. Use `rdd_data.partial.csv` (37k
   rows, all years) if you need the full universe.
3. **`TOPIC_SIMILARITY_MIN` is overridable** via the `TOPIC_SIM_MIN` env var.
   The result is sensitive to it. See `STUDY_PROCESS.txt` Section 12.
4. **`rddensity` API:** `r.test` is a pandas Series indexed
   `['t_asy','t_jk','p_asy','p_jk']`; asymptotic entries are NaN by default, so
   report the jackknife pair. In R it is a **list**, so `$t_jk`/`$p_jk`.
5. **`rdrobust` manual bandwidth:** Python wants `bwselect=""`; R rejects an
   empty string, so omit `bwselect` entirely when passing `h`.
6. **`pandas.iterrows` upcasts ints to floats**, breaking `{:d}` formatting.
7. **The pooled density test is not interpretable as a manipulation test** until
   B2 is done — but it is also not the "artifact" the paper currently claims.

---

## 8. Reproduction

```bash
cd ~/rdd-paper
. .venv/bin/activate

# Stage 1 (warm cache: ~6 min, 9 HTTP requests)
SEC_USER_AGENT="Jokubas Narvydas jokubasnarvydas@gmail.com" \
  python -u 01_scrape_edgar.py \
  --start-date 2022-01-01 --end-date 2025-12-31 \
  --max-filings 0 --min-obs 0 --output rdd_data.csv

# Stage 2
python 02_rdd_analysis.py
python 02b_multi_cutoff_rd.py
python 02c_robustness.py

# sensitivity (each ~7 min)
TOPIC_SIM_MIN=0.4 python 01_scrape_edgar.py ... --output rdd_data_t40.csv
TOPIC_SIM_MIN=0.6 python 01_scrape_edgar.py ... --output rdd_data_t60.csv
```

R (stale, needs `export R_LIBS_USER=~/R/library`):
`~/.local/bin/Rscript 02_rdd_analysis.R` and `02b_multi_cutoff_rd.R`.

---

## 9. The honest bottom line

The raw discontinuity is real and statistically significant: proposals just
below the bar return to a ballot about 5–7% of the time, those just above about
18–20%. That survives clustering.

But the formal RD estimate is 0.078 with an SE of 0.081, its MDE is 22.8pp, it is
null at the narrowest bandwidth, and the pooled figure contradicts the
inverse-variance average of the per-bar jumps by 9 percentage points.

The defensible claim is:

> Proposals that miss the bar return to a ballot roughly 5–7% of the time; those
> that clear it, 18–20%. The difference is large and significant in the raw data,
> but the formal RD estimate is imprecise and sensitive to bandwidth, so the
> discontinuity cannot be cleanly separated from a smooth gradient in support.

Anything stronger than that is not supported by the current analysis.
