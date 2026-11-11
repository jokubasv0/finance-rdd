# Stage 2b -- pooled multi-cutoff RD

Pooled sample 2077 proposals across three thresholds, 431 firms, SEs clustered on CIK.

## Sample by threshold

| Group | n | Firms | near ±2pp | refile rate |
|---|---|---|---|---|
| 5% bar (voted once) | 1274 | 394 | 93 | 0.163 |
| 15% bar (voted twice) | 292 | 155 | 24 | 0.257 |
| 25% bar (voted 3+) | 511 | 105 | 26 | 0.556 |

## Pooled estimates

| Specification | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| pooled, FE | 0.158 | 0.081 | 0.052 | [-0.001, 0.318] | 271/314 |
| pooled, FE + covariates | 0.182 | 0.084 | 0.030 | [0.017, 0.346] | 259/295 |
| pooled, no adjustment | 0.148 | 0.088 | 0.092 | [-0.024, 0.321] | 278/329 |

## Per-threshold estimates

| Group | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 5% bar (voted once) | 0.030 | 0.092 | 0.742 | [-0.150, 0.210] | 166/213 |
| 15% bar (voted twice) | 0.166 | 0.286 | 0.562 | [-0.394, 0.725] | 41/40 |
| 25% bar (voted 3+) | 0.208 | 0.218 | 0.339 | [-0.218, 0.635] | 45/53 |

## Density tests

| Sample | t | p |
|---|---|---|
| 5% bar (voted once) | 0.634 | 0.526 |
| 15% bar (voted twice) | 0.830 | 0.407 |
| 25% bar (voted 3+) | 0.245 | 0.806 |
| POOLED | 1.921 | 0.055 |
