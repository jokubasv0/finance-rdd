# Stage 2b -- pooled multi-cutoff RD

Pooled sample 2052 proposals across three thresholds, 430 firms, SEs clustered on CIK.

## Sample by threshold

| Group | n | Firms | near ±2pp | refile rate |
|---|---|---|---|---|
| 5% bar (voted once) | 1402 | 406 | 109 | 0.149 |
| 15% bar (voted twice) | 298 | 149 | 29 | 0.228 |
| 25% bar (voted 3+) | 352 | 87 | 15 | 0.457 |

## Pooled estimates

| Specification | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| pooled, FE | 0.085 | 0.073 | 0.244 | [-0.058, 0.229] | 300/369 |
| pooled, FE + covariates | 0.107 | 0.075 | 0.151 | [-0.039, 0.253] | 293/362 |
| pooled, no adjustment | 0.092 | 0.078 | 0.241 | [-0.062, 0.245] | 298/360 |

## Per-threshold estimates

| Group | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 5% bar (voted once) | -0.030 | 0.088 | 0.735 | [-0.203, 0.143] | 201/240 |
| 15% bar (voted twice) | 0.110 | 0.246 | 0.654 | [-0.372, 0.593] | 35/37 |
| 25% bar (voted 3+) | -0.004 | 0.224 | 0.985 | [-0.442, 0.434] | 38/47 |

## Density tests

| Sample | t | p |
|---|---|---|
| 5% bar (voted once) | -0.598 | 0.550 |
| 15% bar (voted twice) | 0.496 | 0.620 |
| 25% bar (voted 3+) | 0.567 | 0.571 |
| POOLED | 2.067 | 0.039 |
