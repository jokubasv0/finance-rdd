# Stage 2 results

RD sample: 292 proposals on their second appearance in five years.
MSE-optimal bandwidth h* = 0.0677.

## Main result

| Specification | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| Local linear, conventional | 0.158 | 0.254 | 0.534 | [-0.340, 0.656] | 36/35 |
| Local linear, bias-corrected | 0.137 | 0.313 | 0.663 | [-0.478, 0.751] | 36/35 |

## McCrary density test

Statistic 0.830, p = 0.407. PASS -- no evidence of sorting around the cutoff.

## Bandwidth sensitivity

| h / h* | tau | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 0.50 | 0.229 | 0.368 | 0.533 | [-0.492, 0.951] | 19/19 |
| 0.75 | 0.131 | 0.299 | 0.662 | [-0.455, 0.716] | 26/26 |
| 1.00 | 0.158 | 0.254 | 0.534 | [-0.340, 0.656] | 36/35 |
| 1.25 | 0.164 | 0.222 | 0.460 | [-0.271, 0.598] | 46/43 |
| 1.50 | 0.174 | 0.206 | 0.398 | [-0.230, 0.579] | 54/49 |
| 2.00 | 0.223 | 0.178 | 0.210 | [-0.126, 0.572] | 65/74 |

## Covariate balance

| Covariate | tau | SE | p |
|---|---|---|---|
| log_assets | 0.605 | 1.145 | 0.597 |
| leverage | 0.130 | 0.142 | 0.362 |
| roa | -0.032 | 0.035 | 0.357 |

## Placebo cutoffs

| Vote share | tau | SE | p |
|---|---|---|---|
| 10% | 0.159 | 0.216 | 0.464 |
| 20% | -0.147 | 0.319 | 0.644 |

## Right-censoring robustness

31 observations dropped from the main specification because the next annual meeting is not yet observable. Setting them to zero:

tau = 0.157 (SE 0.212, p 0.459), n = 40/35.

