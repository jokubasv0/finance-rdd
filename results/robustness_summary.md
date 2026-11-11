# Stage 2c -- robustness suite

Usable observations 2032, 430 firms, 23 duplicates dropped.

| Specification | tau | SE | p | 95% CI | n |
|---|---|---|---|---|---|
| 1. baseline (FE + covariates) | 0.097 | 0.073 | 0.186 | [-0.046, 0.240] | 2032 |
| 2. + year FE | 0.073 | 0.070 | 0.303 | [-0.066, 0.211] | 2032 |
| 3. + topic FE | 0.133 | 0.073 | 0.067 | [-0.009, 0.275] | 2032 |
| 4. + year FE + topic FE | 0.110 | 0.070 | 0.118 | [-0.028, 0.248] | 2032 |
| 5. + FE both, no covariates | 0.084 | 0.068 | 0.215 | [-0.049, 0.217] | 2032 |
| 6. 25% bar = 3rd submission only | 0.087 | 0.066 | 0.191 | [-0.043, 0.216] | 1780 |
| 7. drop 5% bar | 0.254 | 0.151 | 0.092 | [-0.042, 0.551] | 642 |

Range: tau in [0.073, 0.254]. Significant at 5% in 0/7.
