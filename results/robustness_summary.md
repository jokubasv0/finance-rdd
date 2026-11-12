# Stage 2c -- robustness suite

Usable observations 1583, 427 firms, 23 duplicates dropped.

| Specification | tau | SE | p | 95% CI | n |
|---|---|---|---|---|---|
| 1. baseline (FE + covariates) | 0.080 | 0.081 | 0.324 | [-0.079, 0.239] | 1583 |
| 2. + year FE | 0.058 | 0.078 | 0.460 | [-0.095, 0.211] | 1583 |
| 3. + topic FE | 0.104 | 0.078 | 0.181 | [-0.048, 0.257] | 1583 |
| 4. + year FE + topic FE | 0.079 | 0.075 | 0.292 | [-0.068, 0.226] | 1583 |
| 5. + FE both, no covariates | 0.066 | 0.074 | 0.374 | [-0.079, 0.210] | 1583 |
| 6. 25% bar = 3rd submission only | 0.059 | 0.075 | 0.434 | [-0.088, 0.205] | 1502 |
| 7. drop 5% bar | 0.264 | 0.151 | 0.080 | [-0.032, 0.560] | 459 |

Range: tau in [0.058, 0.264]. Significant at 5% in 0/7.
