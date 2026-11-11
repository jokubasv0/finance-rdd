#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# Stage 2 -- Regression discontinuity analysis of SEC Rule 14a-8(i)(12).
#
# R equivalent of 02_rdd_analysis.py (single-cutoff, 15% bar). The Python
# script is the one that actually produced the reported numbers, because R is
# not installed on this machine and rdrobust/rddensity contain Fortran that
# needs gfortran to compile. The two implementations call the same algorithms
# with the same defaults, so this reproduces the Python output exactly once R
# and gfortran are available:
#
#   sudo apt install r-base gfortran
#   Rscript -e 'install.packages(c("rdrobust","rddensity"))'
#   Rscript 02_rdd_analysis.R
#
# Running variable : run_var = vote_share - 0.15, for proposals on their SECOND
#                    appearance in five years (in_15pct_sample).
# Outcome          : refiled_t1, whether the proponent resubmitted the same
#                    topic at the next annual meeting.
# Cutoff           : 0. Below it the company MAY exclude the third submission;
#                    at or above it, it may not.
# ---------------------------------------------------------------------------

suppressPackageStartupMessages({
  library(rdrobust)
  library(rddensity)
})

CUTOFF       <- 0
OUTCOME      <- "refiled_t1"
COVARIATES   <- c("log_assets", "leverage", "roa")
BW_MULTS     <- c(0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
PLACEBO_CUTS <- c(-0.05, 0.05)   # vote shares of 10% and 20%
LEVEL        <- 95

DATA   <- "rdd_data.csv"
OUTDIR <- "results"

stars <- function(p) {
  if (is.na(p)) "" else if (p < 0.01) "***" else if (p < 0.05) "**" else if (p < 0.10) "*" else ""
}

# Flatten an rdrobust object into a one-row data frame.
# rdrobust returns three rows of estimates: conventional, bias-corrected, robust.
tidy_rd <- function(r) {
  data.frame(
    tau      = r$coef[1, 1], se      = r$se[1, 1], p      = r$pv[1, 1],
    ci_lo    = r$ci[1, 1],   ci_hi   = r$ci[1, 2],
    tau_bc   = r$coef[3, 1], se_bc   = r$se[3, 1], p_bc   = r$pv[3, 1],
    ci_lo_bc = r$ci[3, 1],   ci_hi_bc = r$ci[3, 2],
    h        = r$bws[1, 1],  b       = r$bws[1, 2],
    n_left   = r$N_h[1],     n_right = r$N_h[2],
    stringsAsFactors = FALSE
  )
}

fit_rd <- function(y, x, c = CUTOFF, p = 1, h = NULL) {
  if (is.null(h)) {
    r <- rdrobust(y = y, x = x, c = c, p = p, q = p + 1,
                  bwselect = "mserd", vce = "nn", level = LEVEL)
  } else {
    # Fixed bandwidth: pass h and b only. Supplying bwselect here would be an
    # error -- R's rdrobust rejects an empty bwselect string and ignores the
    # selector whenever h is given anyway.
    r <- rdrobust(y = y, x = x, c = c, p = p, q = p + 1,
                  h = h, b = h, vce = "nn", level = LEVEL)
  }
  tidy_rd(r)
}

fmt <- function(d) {
  sprintf("%7.3f%-3s SE %6.3f  p %5.3f  95%% CI [%6.3f, %6.3f]  n %d/%d",
          d$tau, stars(d$p), d$se, d$p, d$ci_lo, d$ci_hi, d$n_left, d$n_right)
}

# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------
if (!file.exists(DATA)) stop(sprintf("%s not found. Run 01_scrape_edgar.py first.", DATA))
raw <- read.csv(DATA, stringsAsFactors = FALSE)

if ("data_source" %in% names(raw)) {
  bad <- setdiff(unique(raw$data_source), "EDGAR")
  if (length(bad) > 0) warning("dataset contains non-EDGAR rows: ",
                               paste(bad, collapse = ", "))
}

# RD sample: proposals on their second appearance in five years. refiled_t1 is
# right-censored for recent votes (next annual meeting not yet held); those rows
# are dropped here and reinstated as zeros in the robustness block.
sample_all <- raw[raw$in_15pct_sample %in% c(TRUE, "True", "true"), ]
sample_all[[OUTCOME]] <- suppressWarnings(as.numeric(sample_all[[OUTCOME]]))
n_censored <- sum(is.na(sample_all[[OUTCOME]]))
df <- sample_all[!is.na(sample_all[[OUTCOME]]) & !is.na(sample_all$run_var), ]

if (nrow(df) < 30) stop(sprintf("only %d usable observations.", nrow(df)))

dir.create(OUTDIR, showWarnings = FALSE)

cat(strrep("=", 78), "\n")
cat(" STAGE 2 -- RDD ANALYSIS OF RULE 14a-8(i)(12) RESUBMISSION THRESHOLD\n")
cat(strrep("=", 78), "\n")
cat(sprintf(" RD sample (2nd vote) : %d\n", nrow(df)))
cat(sprintf("   dropped, censored  : %d\n", n_censored))
cat(sprintf("   below 15%%          : %d\n", sum(df$run_var < CUTOFF)))
cat(sprintf("   at/above 15%%       : %d\n", sum(df$run_var >= CUTOFF)))
cat(sprintf("   within +/-2pp      : %d\n", sum(abs(df$run_var) <= 0.02)))
cat(sprintf("   within +/-5pp      : %d\n", sum(abs(df$run_var) <= 0.05)))

# ---- 1. descriptives -------------------------------------------------------
cat("\n", strrep("-", 78), "\n 1. DESCRIPTIVE STATISTICS BY SIDE OF THE CUTOFF\n",
    strrep("-", 78), "\n", sep = "")
desc <- do.call(rbind, lapply(
  list(c("Below 15%", TRUE), c("At/above 15%", FALSE)),
  function(g) {
    below <- as.logical(g[2])
    d <- if (below) df[df$run_var < CUTOFF, ] else df[df$run_var >= CUTOFF, ]
    data.frame(group = g[1], n = nrow(d),
               refile_rate = mean(d[[OUTCOME]]),
               vote_share  = mean(d$vote_share),
               log_assets  = mean(d$log_assets, na.rm = TRUE),
               leverage    = mean(d$leverage,  na.rm = TRUE),
               roa         = mean(d$roa,       na.rm = TRUE),
               stringsAsFactors = FALSE)
  }))
print(desc, row.names = FALSE, digits = 3)
write.csv(desc, file.path(OUTDIR, "01_descriptives.csv"), row.names = FALSE)

# ---- 2. McCrary ------------------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 2. MCCRARY DENSITY TEST  (H0: no manipulation of the running variable)\n",
    strrep("-", 78), "\n", sep = "")
dens <- rddensity(X = df$run_var, c = CUTOFF)
# rddensity returns `test` as a LIST with $t_asy/$t_jk/$p_asy/$p_jk. The
# asymptotic entries are NA under the default binned setup, so the jackknife
# pair is the one to report (matches the Python port, which exposes the same
# fields through a pandas Series).
t_stat <- dens$test$t_jk
p_val  <- dens$test$p_jk
cat(sprintf(" test statistic       : %.3f\n", t_stat))
cat(sprintf(" p-value              : %.3f\n", p_val))
cat(sprintf(" verdict              : %s\n",
            if (p_val > 0.10)
              "PASS -- no evidence of sorting around the cutoff"
            else "FLAG -- density discontinuity, investigate"))
write.csv(data.frame(test_stat = t_stat, p_value = p_val),
          file.path(OUTDIR, "02_mccrary.csv"), row.names = FALSE)

# ---- 3. baseline -----------------------------------------------------------
y <- as.numeric(df[[OUTCOME]])
x <- as.numeric(df$run_var)

base <- fit_rd(y, x, p = 1)
cat("\n", strrep("-", 78),
    "\n 3. BASELINE LOCAL LINEAR RD  (p=1, MSERD bandwidth)\n",
    strrep("-", 78), "\n", sep = "")
cat(sprintf(" h*                   : %.4f   (bias bandwidth %.4f)\n", base$h, base$b))
cat(sprintf(" conventional         : %s\n", fmt(base)))
cat(sprintf(" bias-corrected       : %7.3f%-3s SE %6.3f  p %5.3f  95%% CI [%6.3f, %6.3f]\n",
            base$tau_bc, stars(base$p_bc), base$se_bc, base$p_bc,
            base$ci_lo_bc, base$ci_hi_bc))
cat(sprintf(" interpretation       : effect of eligibility is %s at 5%% (p=%.3f)\n",
            if (base$p_bc < 0.05) "significant"
            else if (base$p_bc < 0.10) "marginally significant"
            else "NOT significant", base$p_bc))
write.csv(base, file.path(OUTDIR, "03_baseline.csv"), row.names = FALSE)

# ---- 4. bandwidth sensitivity ---------------------------------------------
cat("\n", strrep("-", 78), "\n 4. BANDWIDTH SENSITIVITY\n", strrep("-", 78), "\n", sep = "")
grid <- do.call(rbind, lapply(BW_MULTS, function(m) {
  d <- fit_rd(y, x, h = base$h * m)
  d$multiplier <- m
  d
}))
for (i in seq_len(nrow(grid))) {
  g <- grid[i, ]
  cat(sprintf(" %4.2fx h*  h=%.4f  %s\n", g$multiplier, g$h, fmt(g)))
}
cat(sprintf(" sign stability       : %s\n",
            if (length(unique(sign(grid$tau))) == 1) "stable" else "UNSTABLE across bandwidths"))
write.csv(grid, file.path(OUTDIR, "04_bandwidth_sensitivity.csv"), row.names = FALSE)

# ---- 5. covariate balance --------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 5. COVARIATE BALANCE  (placebo outcomes; expect no effect)\n",
    strrep("-", 78), "\n", sep = "")
bal <- do.call(rbind, lapply(COVARIATES, function(cov) {
  sub <- df[!is.na(df[[cov]]), ]
  if (nrow(sub) < 20) return(NULL)
  d <- fit_rd(as.numeric(sub[[cov]]), as.numeric(sub$run_var), h = base$h)
  d$covariate <- cov
  cat(sprintf(" %-12s tau=%7.3f se=%7.3f p=%6.3f%s\n", cov, d$tau, d$se, d$p,
              if (d$p < 0.10) "  <-- IMBALANCE" else ""))
  d
}))
write.csv(bal, file.path(OUTDIR, "05_covariate_balance.csv"), row.names = FALSE)

# ---- 6. placebo cutoffs ----------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 6. PLACEBO CUTOFFS  (expect no effect away from 15%)\n",
    strrep("-", 78), "\n", sep = "")
plc <- do.call(rbind, lapply(PLACEBO_CUTS, function(cc) {
  d <- fit_rd(y, x, c = cc, h = base$h)
  d$placebo_cutoff <- cc
  d$vote_share <- 0.15 + cc
  cat(sprintf(" vote share %5.1f%%  tau=%7.3f se=%7.3f p=%6.3f%s\n",
              d$vote_share * 100, d$tau, d$se, d$p,
              if (d$p < 0.10) "  <-- unexpected effect" else ""))
  d
}))
write.csv(plc, file.path(OUTDIR, "06_placebo_cutoffs.csv"), row.names = FALSE)

# ---- 7. polynomial order ---------------------------------------------------
cat("\n", strrep("-", 78),
    "\n 7. POLYNOMIAL ORDER SENSITIVITY\n", strrep("-", 78), "\n", sep = "")
poly <- do.call(rbind, lapply(c(1, 2), function(p) {
  d <- fit_rd(y, x, p = p)
  d$polynomial_order <- p
  cat(sprintf(" p=%d  h=%.4f  tau=%7.3f%-3s se=%7.3f  p=%6.3f  n=%d/%d\n",
              p, d$h, d$tau, stars(d$p), d$se, d$p, d$n_left, d$n_right))
  d
}))
write.csv(poly, file.path(OUTDIR, "07_polynomial_sensitivity.csv"), row.names = FALSE)

# ---- 8. right-censoring robustness ----------------------------------------
cat("\n", strrep("-", 78),
    "\n 8. RIGHT-CENSORING ROBUSTNESS\n", strrep("-", 78), "\n", sep = "")
cat(sprintf(" %d observations have an unobservable t+1 outcome; set to 0 here.\n", n_censored))
cens <- sample_all[!is.na(sample_all$run_var), ]
cens[[OUTCOME]][is.na(cens[[OUTCOME]])] <- 0
cens_res <- fit_rd(as.numeric(cens[[OUTCOME]]), as.numeric(cens$run_var), p = 1)
cat(sprintf(" censored as 0        : %s\n", fmt(cens_res)))
cat(sprintf(" sign vs main spec    : %s\n",
            if (sign(cens_res$tau) == sign(base$tau)) "same" else "FLIPPED"))
write.csv(cens_res, file.path(OUTDIR, "08_censoring_robustness.csv"), row.names = FALSE)

cat("\n", strrep("=", 78), "\n", sprintf(" written to %s/\n", OUTDIR),
    strrep("=", 78), "\n", sep = "")
