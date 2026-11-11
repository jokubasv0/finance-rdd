# Stage 2 results

RD sample: 298 proposals on their second appearance in five years.
MSE-optimal bandwidth h* = 0.0556.

## Main result

| Specification | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| Local linear, conventional | 0.166 | 0.233 | 0.477 | [-0.291, 0.623] | 31/34 |
| Local linear, bias-corrected | 0.116 | 0.270 | 0.668 | [-0.414, 0.646] | 31/34 |

## McCrary density test

Statistic 0.496, p = 0.620. PASS -- no evidence of sorting around the cutoff.

## Bandwidth sensitivity

| h / h* | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 0.50 | 0.171 | 0.298 | 0.566 | [-0.413, 0.756] | 18/23 |
| 0.75 | 0.168 | 0.257 | 0.514 | [-0.337, 0.672] | 24/31 |
| 1.00 | 0.166 | 0.233 | 0.477 | [-0.291, 0.623] | 31/34 |
| 1.25 | 0.189 | 0.205 | 0.357 | [-0.213, 0.591] | 42/40 |
| 1.50 | 0.250 | 0.180 | 0.166 | [-0.104, 0.604] | 49/49 |
| 2.00 | 0.296 | 0.154 | 0.055 | [-0.006, 0.598] | 64/68 |

## Covariate balance

| Covariate | tau | SE | p |
|---|---|---|---|
| log_assets | 0.596 | 1.145 | 0.603 |
| leverage | 0.193 | 0.107 | 0.071 |
| roa | -0.044 | 0.031 | 0.162 |

## Placebo cutoffs

| Vote share | tau | SE | p |
|---|---|---|---|
| 10% | -0.078 | 0.051 | 0.123 |
| 20% | -0.058 | 0.347 | 0.866 |

## Right-censoring robustness

32 observations dropped from the main specification because the next annual meeting is not yet observable. Setting them to zero:

tau = 0.135 (SE 0.205, p 0.513), n = 35/36.

