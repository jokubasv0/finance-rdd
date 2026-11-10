# Handoff — resume here

State as of the night the scrape completed. Everything below is committed
locally in `~/rdd-paper`. Nothing is running; nothing is half-written.

## Where things stand

| Stage | Status |
|---|---|
| 1. EDGAR scrape | ✅ done, `rdd_data.csv`, 2,294 obs, 100% real EDGAR data |
| 2. RD analysis (Python) | ✅ done, all 8 tests run, `results/` |
| 3. Paper draft | ⬜ not started |
| Push to GitHub | ⬜ blocked: repo does not exist yet |

## Open decision (blocks Stage 3)

Stage 2 is methodologically clean but **underpowered**: MDE ≈ 88pp, effective
n inside the bandwidth = 71. Coefficient is positive and sign-stable
(0.13–0.23) but never significant (p = 0.66). Three ways forward:

1. **Pool all three thresholds** (5%, 15%, 25%). n goes 292 → 2,077, obs within
   ±2pp go 24 → 143. MDE drops to roughly 25pp. Requires multi-cutoff RD with
   threshold fixed effects, plus per-cutoff reporting. Assumption: the effect of
   "you may be excluded" is comparable across bars. Best chance of a real result.
2. **Keep 15% only, report honestly as underpowered.** Fastest and purest, but
   a thin paper.
3. **Change the outcome** to "was the proposal actually excluded" (the first
   stage) instead of "did the proponent refile". Cleaner signal, avoids noise
   from the fuzzy topic matching.

## To push (one action needed from you)

The GitHub token is fine-grained and cannot create repositories:

```
GraphQL: Resource not accessible by personal access token (createRepository)
```

Create an **empty private** repo named `rdd-paper` at github.com (no README, no
.gitignore, no licence — it must be empty), then:

```bash
cd ~/rdd-paper
git remote add origin https://github.com/<your-username>/rdd-paper.git
git push -u origin main
```

If the remote is already configured, only the push is needed.

## Things worth checking when you resume

- **Label noise.** 75th percentile of `vote_share` is 0.94 while the median is
  0.31. Some near-unanimous rows may be management proposals misclassified as
  shareholder proposals because a nearby sentence mentions "proposal". Does not
  affect the 15% RD sample, but worth tightening `is_shareholder_proposal`.
- **Fuzzy refiling.** `refiled_t1` links proposals by Jaccard similarity of
  title tokens (threshold 0.5). Both false negatives and false positives.
- **Right-censoring.** 31 observations (all 2025 votes) have an unobservable
  t+1 outcome because the next annual meeting has not been held. Dropped in the
  main spec, reinstated as zeros in the robustness block (sign unchanged).
- **Unverified claim** in the Stage 1 docstring: that the SEC proposed
  rescinding Rule 14a-8 in September 2026. Verify before it goes in the paper.

## Commands

```bash
cd ~/rdd-paper
. .venv/bin/activate
python 02_rdd_analysis.py          # reruns all of Stage 2, writes results/
python 01_scrape_edgar.py --self-test
```

## Commit log

```
32f6337 Stage 2: RD analysis in Python (rdrobust/rddensity ports)
4f5ed2c Stage 1: EDGAR 14a-8 vote scraper and RD sample
```
