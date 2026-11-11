# Stage 2b -- pooled multi-cutoff RD

Pooled sample 2047 proposals across three thresholds, 429 firms, SEs clustered on CIK.

## Sample by threshold

| Group | n | Firms | near ±2pp | refile rate |
|---|---|---|---|---|
| 5% bar (voted once) | 1478 | 414 | 117 | 0.131 |
| 15% bar (voted twice) | 316 | 145 | 32 | 0.184 |
| 25% bar (voted 3+) | 253 | 75 | 12 | 0.526 |

## Pooled estimates

| Specification | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| pooled, FE | 0.138 | 0.059 | 0.018 | [0.024, 0.253] | 288/329 |
| pooled, FE + covariates | 0.158 | 0.058 | 0.007 | [0.043, 0.272] | 279/312 |
| pooled, no adjustment | 0.123 | 0.062 | 0.049 | [0.001, 0.245] | 287/323 |

## Per-threshold estimates

| Group | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 5% bar (voted once) | 0.076 | 0.056 | 0.177 | [-0.034, 0.186] | 215/257 |
| 15% bar (voted twice) | 0.450 | 0.148 | 0.002 | [0.159, 0.741] | 54/58 |
| 25% bar (voted 3+) | -0.144 | 0.217 | 0.507 | [-0.571, 0.282] | 31/42 |

## Density tests

| Sample | t | p |
|---|---|---|
| 5% bar (voted once) | -0.638 | 0.523 |
| 15% bar (voted twice) | -0.430 | 0.667 |
| 25% bar (voted 3+) | 0.032 | 0.974 |
| POOLED | -1.132 | 0.257 |
