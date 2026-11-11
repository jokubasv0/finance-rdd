# Stage 2b -- pooled multi-cutoff RD

Pooled sample 2059 proposals across three thresholds, 430 firms, SEs clustered on CIK.

## Sample by threshold

| Group | n | Firms | near ±2pp | refile rate |
|---|---|---|---|---|
| 5% bar (voted once) | 1312 | 403 | 103 | 0.166 |
| 15% bar (voted twice) | 349 | 154 | 31 | 0.258 |
| 25% bar (voted 3+) | 398 | 99 | 16 | 0.462 |

## Pooled estimates

| Specification | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| pooled, FE | 0.126 | 0.072 | 0.080 | [-0.015, 0.266] | 316/397 |
| pooled, FE + covariates | 0.140 | 0.072 | 0.052 | [-0.001, 0.281] | 306/379 |
| pooled, no adjustment | 0.133 | 0.082 | 0.106 | [-0.028, 0.293] | 283/331 |

## Per-threshold estimates

| Group | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 5% bar (voted once) | -0.019 | 0.092 | 0.840 | [-0.200, 0.162] | 189/234 |
| 15% bar (voted twice) | 0.399 | 0.195 | 0.041 | [0.017, 0.780] | 55/49 |
| 25% bar (voted 3+) | 0.058 | 0.240 | 0.808 | [-0.411, 0.528] | 50/58 |

## Density tests

| Sample | t | p |
|---|---|---|
| 5% bar (voted once) | -0.408 | 0.683 |
| 15% bar (voted twice) | 1.242 | 0.214 |
| 25% bar (voted 3+) | 0.441 | 0.659 |
| POOLED | 3.113 | 0.002 |
