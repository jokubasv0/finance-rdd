# Stage 2b -- pooled multi-cutoff RD

Pooled sample 1603 proposals across three thresholds, 427 firms, SEs clustered on CIK.

## Sample by threshold

| Group | n | Firms | near ±2pp | refile rate |
|---|---|---|---|---|
| 5% bar (voted once) | 1136 | 402 | 108 | 0.173 |
| 15% bar (voted twice) | 283 | 150 | 31 | 0.258 |
| 25% bar (voted 3+) | 184 | 79 | 14 | 0.478 |

## Pooled estimates

| Specification | tau | SE | p | 95% CI | n (L/R) | MDE |
|---|---|---|---|---|---|---|
| pooled, FE | 0.068 | 0.080 | 0.396 | [-0.089, 0.225] | 261/253 | 0.224 |
| pooled, FE + covariates | 0.078 | 0.081 | 0.337 | [-0.081, 0.237] | 253/245 | 0.228 |
| pooled, no adjustment | 0.051 | 0.083 | 0.542 | [-0.112, 0.213] | 261/253 | 0.232 |

## Per-threshold estimates

| Group | tau | SE | p | 95% CI | n (L/R) | MDE |
|---|---|---|---|---|---|---|
| 5% bar (voted once) | -0.028 | 0.088 | 0.752 | [-0.200, 0.145] | 201/182 | 0.246 |
| 15% bar (voted twice) | 0.110 | 0.231 | 0.634 | [-0.343, 0.563] | 37/40 | 0.647 |
| 25% bar (voted 3+) | -0.019 | 0.206 | 0.925 | [-0.423, 0.384] | 18/35 | 0.577 |

Inverse-variance weighted average of the per-bar jumps: **-0.012** (SE 0.076). The pooled estimate imposes a common bandwidth and polynomial across bars and is not an average of these jumps; the two should be read together.


## Density tests

| Sample | t | p |
|---|---|---|
| 5% bar (voted once) | -0.432 | 0.666 |
| 15% bar (voted twice) | 0.421 | 0.674 |
| 25% bar (voted 3+) | 0.812 | 0.417 |
| POOLED | 2.378 | 0.017 |
