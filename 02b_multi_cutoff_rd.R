#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# Stage 2b -- Multi-cutoff RD pooling all three 14a-8(i)(12) bars.
#
# R equivalent of 02b_multi_cutoff_rd.py. The three bars (5% after one vote,
# 15% after two, 25% after three or more) share the same structure, so they
# stack into a single running variable once centred on each proposal's own bar.
# Pooling takes the sample from 292 to 2077.
#
# Requires: rdrobust, rddensity
#   Rscript -e 'install.packages(c("rdrobust","rddensity"))'
#   Rscript 02b_multi_cutoff_rd.R
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(rdrobust)
  library(rddensity)
})

CUTOFF     <- 0
OUTCOME    <- "refiled_t1"
COVARIATES <- c("log_assets", "leverage", "roa")
BW_MULTS   <- c(0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
PLACEBO    <- c(-0.05, 0.05)
LEVEL      <- 95
DATA       <- "rdd_data.csv"
OUTDIR     <- "results"

stars <- function(p) {
  if (is.na(p)) "" else if (p < 0.01) "***" else if (p < 0.05) "**" else if (p < 0.10) "*" else ""
}

tidy_rd <- function(r) {
  data.frame(
    tau = r$coef[1, 1], se = r$se[1, 1], p = r$pv[1, 1],
    ci_lo = r$ci[1, 1], ci_hi = r$ci[1, 2],
    tau_bc = r$coef[3, 1], se_bc = r$se[3, 1], p_bc = r$pv[3, 1],
    ci_lo_bc = r$ci[3, 1], ci_hi_bc = r$ci[3, 2],
    h = r$bws[1, 1], b = r$bws[1, 2],
    n_left = r$N_h[1], n_right = r$N_h[2],
    stringsAsFactors = FALSE
  )
}

fit_rd <- function(y, x, covs = NULL, cluster = NULL, c = CUTOFF, p = 1, h = NULL) {
  args <- list(y = y, x = x, c = c, p = p, q = p + 1, vce = "nn", level = LEVEL)
  if (!is.null(covs))    args$covs    <- covs
  if (!is.null(cluster)) args$cluster <- cluster
  if (is.null(h)) {
    args$bwselect <- "mserd"
  } else {
    args$h <- h
    args$b <- h
  }
  tidy_rd(do.call(rdrobust, args))
}

fmt <- function(d) {
  sprintf("%7.3f%-3s SE %6.3f  p %5.3f  95%% CI [%6.3f, %6.3f]  n %d/%d",
          d$tau_bc, stars(d$p_bc), d$se_bc, d$p_bc,
          d$ci_lo_bc, d$ci_hi_bc, d$n_left, d$n_right)
}

# ---------------------------------------------------------------------------
if (!file.exists(DATA)) stop(sprintf("%s not found. Run 01_scrape_edgar.py first.", DATA))
raw <- read.csv(DATA, stringsAsFactors = FALSE)
raw[[OUTCOME]] <- suppressWarnings(as.numeric(raw[[OUTCOME]]))

# Map appearance count to the three legal bars. The rule caps at 25% for three
# or more appearances, so counts above three all share the 25% bar.
raw$bar_group <- ifelse(raw$vote_number_5y == 1, 0.05,
                        ifelse(raw$vote_number_5y == 2, 0.15, 0.25))
raw$group_label <- c("5% bar (voted once)", "15% bar (voted twice)",
                     "25% bar (voted 3+)")[match(raw$bar_group, c(0.05, 0.15, 0.25))]

censored <- sum(is.na(raw[[OUTCOME]]))
df <- raw[!is.na(raw[[OUTCOME]]) & !is.na(raw$vote_share), ]
df$run_var <- df$vote_share - df$bar_group
if (nrow(df) < 100) stop(sprintf("only %d usable observations.", nrow(df)))

dir.create(OUTDIR, showWarnings = FALSE)

cat(strrep("=", 78), "\n")
cat(" STAGE 2b -- MULTI-CUTOFF RD ACROSS ALL THREE 14a-8(i)(12) BARS\n")
cat(strrep("=", 78), "\n")
cat(sprintf(" pooled sample          : %d\n", nrow(df)))
cat(sprintf(" dropped, censored      : %d\n", censored))
cat(sprintf(" unique firms (clusters): %d\n", length(unique(df$cik))))
cat(sprintf(" within +/-2pp          : %d\n", sum(abs(df$run_var) <= 0.02)))
cat(sprintf(" within +/-5pp          : %d\n", sum(abs(df$run_var) <= 0.05)))

y  <- as.numeric(df[[OUTCOME]])
x  <- as.numeric(df$run_var)
cl <- as.character(df$cik)

# Threshold dummies: base category is the 5% bar.
fe <- cbind(as.numeric(df$bar_group == 0.15), as.numeric(df$bar_group == 0.25))
cov_full <- cbind(fe, as.matrix(df[, COVARIATES]))

# ---- 1. descriptives -------------------------------------------------------
cat("\n", strrep("-", 78), "\n 1. SAMPLE BY THRESHOLD\n", strrep("-", 78), "\n", sep = "")
desc <- do.call(rbind, lapply(c("5% bar (voted once)", "15% bar (voted twice)",
                                "25% bar (voted 3+)"), function(g) {
  d <- df[df$group_label == g, ]
  data.frame(group = g, n = nrow(d), firms = length(unique(d$cik)),
             near_2pp = sum(abs(d$run_var) <= 0.02),
             refile_rate = mean(d[[OUTCOME]]),
             vote_share = mean(d$vote_share),
             log_assets = mean(d$log_assets, na.rm = TRUE),
             leverage = mean(d$leverage, na.rm = TRUE),
             roa = mean(d$roa, na.rm = TRUE), stringsAsFactors = FALSE)
}))
print(desc, row.names = FALSE, digits = 3)
write.csv(desc, file.path(OUTDIR, "10_pooled_descriptives.csv"), row.names = FALSE)

# ---- 2. density ------------------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 2. MCCRARY DENSITY TESTS  (H0: no manipulation)\n",
    strrep("-", 78), "\n", sep = "")
dens_row <- function(label, X) {
  r <- rddensity(X = X, c = CUTOFF)
  data.frame(sample = label, test_stat = r$test$t_jk, p_value = r$test$p_jk,
             n = length(X), stringsAsFactors = FALSE)
}
dens <- rbind(
  dens_row("5% bar (voted once)",   df$run_var[df$group_label == "5% bar (voted once)"]),
  dens_row("15% bar (voted twice)", df$run_var[df$group_label == "15% bar (voted twice)"]),
  dens_row("25% bar (voted 3+)",    df$run_var[df$group_label == "25% bar (voted 3+)"]),
  dens_row("POOLED",                df$run_var)
)
for (i in seq_len(nrow(dens))) {
  g <- dens[i, ]
  cat(sprintf(" %-24s t=%6.3f  p=%6.3f  n=%5d  %s\n", g$sample, g$test_stat,
              g$p_value, g$n, if (g$p_value > 0.10) "PASS" else "FLAG"))
}
cat("\n NOTE: the pooled test is not interpretable. Stacking groups whose vote-share\n")
cat(" distributions differ induces a density jump unrelated to manipulation. The\n")
cat(" per-threshold tests are the valid ones.\n")
write.csv(dens, file.path(OUTDIR, "11_pooled_density.csv"), row.names = FALSE)

# ---- 3. pooled -------------------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 3. POOLED RD  (threshold FE; SEs clustered on CIK)\n",
    strrep("-", 78), "\n", sep = "")
specs <- list(
  "pooled, FE"              = fit_rd(y, x, covs = fe,       cluster = cl),
  "pooled, FE + covariates" = fit_rd(y, x, covs = cov_full, cluster = cl),
  "pooled, no adjustment"   = fit_rd(y, x,                    cluster = cl)
)
for (nm in names(specs)) cat(sprintf(" %-28s%s\n", nm, fmt(specs[[nm]])))

# ---- 4. per-threshold ------------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 4. PER-THRESHOLD RD  (no pooling)\n", strrep("-", 78), "\n", sep = "")
per <- do.call(rbind, lapply(c("5% bar (voted once)", "15% bar (voted twice)",
                               "25% bar (voted 3+)"), function(g) {
  d <- df[df$group_label == g, ]
  r <- fit_rd(as.numeric(d[[OUTCOME]]), as.numeric(d$run_var),
              covs = as.matrix(d[, COVARIATES]), cluster = as.character(d$cik))
  cat(sprintf(" %-24s%s\n", g, fmt(r)))
  r$group <- g
  r
}))
write.csv(per, file.path(OUTDIR, "12_per_threshold.csv"), row.names = FALSE)

# ---- 5. bandwidth ----------------------------------------------------------
h_star <- specs[["pooled, FE"]]$h
cat("\n", strrep("-", 78), "\n 5. POOLED BANDWIDTH SENSITIVITY\n", strrep("-", 78), "\n", sep = "")
grid <- do.call(rbind, lapply(BW_MULTS, function(m) {
  r <- fit_rd(y, x, covs = fe, cluster = cl, h = h_star * m)
  r$multiplier <- m
  cat(sprintf(" %4.2fx h*  h=%.4f  tau=%7.3f%-3s SE %6.3f  p %5.3f  n %d/%d\n",
              m, r$h, r$tau, stars(r$p), r$se, r$p, r$n_left, r$n_right))
  r
}))
cat(sprintf(" sign stability: %s\n",
            if (length(unique(sign(grid$tau))) == 1) "stable" else "UNSTABLE"))
write.csv(grid, file.path(OUTDIR, "13_pooled_bandwidth.csv"), row.names = FALSE)

# ---- 6. balance ------------------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 6. POOLED COVARIATE BALANCE\n", strrep("-", 78), "\n", sep = "")
bal <- do.call(rbind, lapply(COVARIATES, function(cv) {
  r <- fit_rd(as.numeric(df[[cv]]), x, covs = fe, cluster = cl)
  cat(sprintf(" %-12s tau=%7.3f SE %6.3f p %5.3f%s\n", cv, r$tau, r$se, r$p,
              if (r$p < 0.10) "  <-- IMBALANCE" else ""))
  r$covariate <- cv
  r
}))
write.csv(bal, file.path(OUTDIR, "14_pooled_balance.csv"), row.names = FALSE)

# ---- 7. placebo ------------------------------------------------------------
cat("\n", strrep("-", 78), "\n 7. POOLED PLACEBO CUTOFFS\n", strrep("-", 78), "\n", sep = "")
plc <- do.call(rbind, lapply(PLACEBO, function(cc) {
  r <- fit_rd(y, x, covs = fe, cluster = cl, c = cc)
  cat(sprintf(" offset %+.2f  tau=%7.3f SE %6.3f p %5.3f%s\n", cc, r$tau, r$se, r$p,
              if (r$p < 0.10) "  <-- unexpected" else ""))
  r$placebo_offset <- cc
  r
}))
write.csv(plc, file.path(OUTDIR, "15_pooled_placebo.csv"), row.names = FALSE)

# ---- 8. polynomial ---------------------------------------------------------
cat("\n", strrep("-", 78), "\n 8. POOLED POLYNOMIAL ORDER\n", strrep("-", 78), "\n", sep = "")
poly <- do.call(rbind, lapply(c(1, 2), function(p) {
  r <- fit_rd(y, x, covs = fe, cluster = cl, p = p)
  cat(sprintf(" p=%d  h=%.4f  tau=%7.3f%-3s SE %6.3f  p %5.3f  n %d/%d\n",
              p, r$h, r$tau_bc, stars(r$p_bc), r$se_bc, r$p_bc, r$n_left, r$n_right))
  r$order <- p
  r
}))
write.csv(poly, file.path(OUTDIR, "16_pooled_polynomial.csv"), row.names = FALSE)

cat("\n", strrep("=", 78), "\n", sprintf(" written to %s/\n", OUTDIR),
    strrep("=", 78), "\n", sep = "")
