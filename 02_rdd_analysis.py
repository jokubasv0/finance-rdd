#!/usr/bin/env python3
"""
Stage 2 -- Regression discontinuity analysis of SEC Rule 14a-8(i)(12).

Running variable : run_var = vote_share - 0.15, within the sample of proposals
                   on their SECOND appearance in five years (in_15pct_sample).
Outcome          : refiled_t1, whether the proponent resubmitted the same topic
                   at the next annual meeting.
Cutoff           : 0. Below it the company MAY exclude the third submission;
                   at or above it, it may not.

Estimators are the official Python ports of the R packages named in the
project spec (rdpackages): rdrobust 2.1.1 and rddensity 3.0. Same algorithms,
same defaults, so 02_rdd_analysis.R reproduces these numbers exactly.

Usage:  python 02_rdd_analysis.py [--data rdd_data.csv] [--outdir results]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from rdrobust import rdrobust
from rddensity import rddensity

CUTOFF = 0.0                      # run_var is already centred on 15%
OUTCOME = "refiled_t1"
COVARIATES = ["log_assets", "leverage", "roa"]
BW_MULTIPLIERS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
PLACEBO_CUTOFFS = [-0.05, 0.05]   # i.e. vote shares of 10% and 20%
ALPHA_LEVEL = 95


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _stars(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def fit_rd(y: np.ndarray, x: np.ndarray, c: float = CUTOFF, p: int = 1,
           h: float | None = None) -> dict:
    """Run rdrobust and flatten the result into a dict of floats."""
    kw = dict(c=c, p=p, q=p + 1, bwselect="mserd", vce="nn", level=ALPHA_LEVEL)
    if h is not None:
        # Fixed bandwidth. rdrobust signals "manual" with an EMPTY bwselect
        # string, not "manual". The bias bandwidth b is pinned to h as well;
        # leaving b unset would let the bias term pick its own scale and break
        # the monotonicity of the sensitivity grid.
        kw.update(h=h, b=h, bwselect="")
    r = rdrobust(y=y, x=x, **kw)
    return {
        "tau": float(r.coef.iloc[0, 0]),
        "se": float(r.se.iloc[0, 0]),
        "p": float(r.pv.iloc[0, 0]),
        "ci_lo": float(r.ci.iloc[0, 0]),
        "ci_hi": float(r.ci.iloc[0, 1]),
        "tau_bc": float(r.coef.iloc[2, 0]),
        "se_bc": float(r.se.iloc[2, 0]),
        "p_bc": float(r.pv.iloc[2, 0]),
        "ci_lo_bc": float(r.ci.iloc[2, 0]),
        "ci_hi_bc": float(r.ci.iloc[2, 1]),
        "h": float(r.bws.iloc[0, 0]),
        "b": float(r.bws.iloc[0, 1]),
        "n_left": int(r.N_h[0]),
        "n_right": int(r.N_h[1]),
    }


def fmt(r: dict, digits: int = 3) -> str:
    return (f"{r['tau']:.{digits}f}{_stars(r['p'])} "
            f"({r['se']:.{digits}f})  "
            f"95% CI [{r['ci_lo']:.{digits}f}, {r['ci_hi']:.{digits}f}]  "
            f"n={r['n_left']}/{r['n_right']}")


# MDE at 80% power for a two-sided 5% test: (z_0.975 + z_0.80) * SE.
MDE_Z = 1.959964 + 0.841621


# ---------------------------------------------------------------------------
# analysis blocks
# ---------------------------------------------------------------------------
def descriptive_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, side in (("Below 15%", df[df.run_var < CUTOFF]),
                       ("At/above 15%", df[df.run_var >= CUTOFF])):
        rows.append({
            "group": name,
            "n": len(side),
            "refile_rate": side[OUTCOME].mean(),
            "vote_share": side.vote_share.mean(),
            "log_assets": side.log_assets.mean(),
            "leverage": side.leverage.mean(),
            "roa": side.roa.mean(),
        })
    return pd.DataFrame(rows)


def mccrary(df: pd.DataFrame) -> dict:
    """Density-discontinuity (manipulation) test. H0: density is continuous.

    rddensity returns a pandas Series with t_asy/p_asy (NaN under the default
    binned setup) and t_jk/p_jk (jackknife). The jackknife variant is the
    package default and the one to report.
    """
    r = rddensity(X=df.run_var.to_numpy(), c=CUTOFF)
    t = r.test
    stat = t.get("t_jk")
    pval = t.get("p_jk")
    if stat is None or not np.isfinite(stat):
        stat, pval = t.get("t_asy"), t.get("p_asy")
    return {
        "test_stat": float(stat),
        "p_value": float(pval),
        "n_left": int(r.n["left"]),
        "n_right": int(r.n["right"]),
        "h_left": float(r.h["left"]),
        "h_right": float(r.h["right"]),
    }


def bandwidth_grid(df: pd.DataFrame, h_star: float) -> pd.DataFrame:
    y, x = df[OUTCOME].to_numpy(float), df.run_var.to_numpy(float)
    out = []
    for m in BW_MULTIPLIERS:
        r = fit_rd(y, x, h=h_star * m)
        out.append({"multiplier": m, "h": r["h"], **r})
    return pd.DataFrame(out)


def covariate_balance(df: pd.DataFrame, h_star: float) -> pd.DataFrame:
    """Placebo outcomes: treatment must not predict pre-determined covariates."""
    x = df.run_var.to_numpy(float)
    out = []
    for cov in COVARIATES:
        if cov not in df.columns:
            continue
        sub = df[[cov, "run_var"]].dropna()
        if len(sub) < 20:
            continue
        r = fit_rd(sub[cov].to_numpy(float), sub.run_var.to_numpy(float), h=h_star)
        out.append({"covariate": cov, **r})
    return pd.DataFrame(out)


def placebo_cutoffs(df: pd.DataFrame, h_star: float) -> pd.DataFrame:
    y, x = df[OUTCOME].to_numpy(float), df.run_var.to_numpy(float)
    out = []
    for c in PLACEBO_CUTOFFS:
        # Keep observations on both sides of the fake cutoff.
        mask = np.ones(len(x), dtype=bool)
        r = fit_rd(y[mask], x[mask], c=c, h=h_star)
        out.append({"placebo_cutoff": c,
                    "vote_share": 0.15 + c, **r})
    return pd.DataFrame(out)


def polynomial_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    y, x = df[OUTCOME].to_numpy(float), df.run_var.to_numpy(float)
    out = []
    for p in (1, 2):
        r = fit_rd(y, x, p=p)
        out.append({"polynomial_order": p, **r})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="rdd_data.csv")
    ap.add_argument("--outdir", default="results")
    args = ap.parse_args(argv)

    path = Path(args.data)
    if not path.exists():
        print(f"ERROR: {path} not found. Run 01_scrape_edgar.py first.", file=sys.stderr)
        return 1

    raw = pd.read_csv(path)
    if "data_source" in raw.columns:
        sources = raw["data_source"].unique().tolist()
        if any(s != "EDGAR" for s in sources):
            print(f"WARNING: dataset contains non-EDGAR rows: {sources}", file=sys.stderr)

    # RD sample: proposals on their second appearance in five years.
    # refiled_t1 is right-censored for recent votes: if the company's next
    # annual meeting has not been held yet, we cannot observe whether the
    # proponent returned. Those rows are dropped in the main specification and
    # reinstated as zeros in the robustness block below.
    sample_all = raw[raw.in_15pct_sample.astype(bool)].copy()
    sample_all[OUTCOME] = pd.to_numeric(sample_all[OUTCOME], errors="coerce")
    n_censored = int(sample_all[OUTCOME].isna().sum())
    df = sample_all[sample_all[OUTCOME].notna() & sample_all.run_var.notna()].copy()

    if len(df) < 30:
        print(f"ERROR: only {len(df)} usable observations.", file=sys.stderr)
        return 1

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    print("=" * 78)
    print(" STAGE 2 -- RDD ANALYSIS OF RULE 14a-8(i)(12) RESUBMISSION THRESHOLD")
    print("=" * 78)
    print(f" data file            : {path}")
    print(f" RD sample (2nd vote) : {len(df)}")
    print(f"   dropped, censored  : {n_censored}  (next meeting not yet observable)")
    print(f"   below 15%          : {(df.run_var < CUTOFF).sum()}")
    print(f"   at/above 15%       : {(df.run_var >= CUTOFF).sum()}")
    print(f"   within +/-2pp      : {((df.run_var.abs() <= 0.02)).sum()}")
    print(f"   within +/-5pp      : {((df.run_var.abs() <= 0.05)).sum()}")
    print(f" filing years         : {sorted(pd.to_datetime(df.filing_date).dt.year.unique())}")

    # ---- 1. descriptive ----
    desc = descriptive_table(df)
    print("\n" + "-" * 78)
    print(" 1. DESCRIPTIVE STATISTICS BY SIDE OF THE CUTOFF")
    print("-" * 78)
    print(desc.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    desc.to_csv(outdir / "01_descriptives.csv", index=False)

    # ---- 2. McCrary ----
    mc = mccrary(df)
    print("\n" + "-" * 78)
    print(" 2. MCCRARY DENSITY TEST  (H0: no manipulation of the running variable)")
    print("-" * 78)
    print(f" test statistic       : {mc['test_stat']:.3f}")
    print(f" p-value              : {mc['p_value']:.3f}")
    print(f" observations L/R     : {mc['n_left']}/{mc['n_right']}")
    print(f" bandwidths L/R       : {mc['h_left']:.4f} / {mc['h_right']:.4f}")
    verdict = ("PASS -- no evidence of sorting around the cutoff"
               if mc["p_value"] > 0.10
               else "FLAG -- density discontinuity, investigate before proceeding")
    print(f" verdict              : {verdict}")
    pd.DataFrame([mc]).to_csv(outdir / "02_mccrary.csv", index=False)

    # ---- 3. baseline ----
    y, x = df[OUTCOME].to_numpy(float), df.run_var.to_numpy(float)
    base = fit_rd(y, x, p=1)
    print("\n" + "-" * 78)
    print(" 3. BASELINE LOCAL LINEAR RD  (p=1, MSERD bandwidth)")
    print("-" * 78)
    print(f" h*                   : {base['h']:.4f}   (bias bandwidth {base['b']:.4f})")
    print(f" conventional         : {fmt(base)}")
    print(f" bias-corrected       : {base['tau_bc']:.3f}{_stars(base['p_bc'])} "
          f"({base['se_bc']:.3f})  "
          f"95% CI [{base['ci_lo_bc']:.3f}, {base['ci_hi_bc']:.3f}]")
    sig = "significant" if base["p_bc"] < 0.05 else (
        "marginally significant" if base["p_bc"] < 0.10 else "NOT significant")
    print(f" interpretation       : effect of eligibility is {sig} at 5% "
          f"(p={base['p_bc']:.3f})")
    # MDE at 80% power, two-sided 5%: (z_{0.975} + z_{0.80}) * SE = 2.802 * SE.
    # A coefficient below its own MDE cannot be distinguished from zero here.
    print(f" minimum detectable effect (80% power): {MDE_Z * base['se_bc']:.3f}")
    pd.DataFrame([base]).to_csv(outdir / "03_baseline.csv", index=False)

    # ---- 4. bandwidth sensitivity ----
    h_star = base["h"]
    grid = bandwidth_grid(df, h_star)
    print("\n" + "-" * 78)
    print(" 4. BANDWIDTH SENSITIVITY")
    print("-" * 78)
    print(f" {'mult':>6} {'h':>8} {'tau':>9} {'se':>8} {'p':>7}  {'95% CI':>18}  {'n L/R':>9}")
    for _, r in grid.iterrows():
        print(f" {r.multiplier:>6.2f} {r.h:>8.4f} {r.tau:>8.3f}{_stars(r.p):<1} "
              f"{r.se:>8.3f} {r.p:>7.3f}  "
              f"[{r.ci_lo:>6.3f}, {r.ci_hi:>6.3f}]  "
              f"{int(r.n_left):>3d}/{int(r.n_right):<3d}")
    signs = set(np.sign(grid.tau))
    print(f" sign stability       : {'stable' if len(signs) == 1 else 'UNSTABLE across bandwidths'}")
    grid.to_csv(outdir / "04_bandwidth_sensitivity.csv", index=False)

    # ---- 5. covariate balance ----
    cb = covariate_balance(df, h_star)
    print("\n" + "-" * 78)
    print(" 5. COVARIATE BALANCE  (placebo outcomes; expect no effect)")
    print("-" * 78)
    for _, r in cb.iterrows():
        flag = "  <-- IMBALANCE" if r.p < 0.10 else ""
        print(f" {r.covariate:<12} tau={r.tau:>8.3f} se={r.se:>7.3f} "
              f"p={r.p:>6.3f}{flag}")
    cb.to_csv(outdir / "05_covariate_balance.csv", index=False)

    # ---- 6. placebo cutoffs ----
    pc = placebo_cutoffs(df, h_star)
    print("\n" + "-" * 78)
    print(" 6. PLACEBO CUTOFFS  (expect no effect away from 15%)")
    print("-" * 78)
    for _, r in pc.iterrows():
        flag = "  <-- unexpected effect" if r.p < 0.10 else ""
        print(f" vote share {r.vote_share:>5.1%}  tau={r.tau:>8.3f} se={r.se:>7.3f} "
              f"p={r.p:>6.3f}{flag}")
    pc.to_csv(outdir / "06_placebo_cutoffs.csv", index=False)

    # ---- 7. polynomial order ----
    poly = polynomial_sensitivity(df)
    print("\n" + "-" * 78)
    print(" 7. POLYNOMIAL ORDER SENSITIVITY")
    print("-" * 78)
    for _, r in poly.iterrows():
        print(f" p={int(r.polynomial_order)}  h={r.h:.4f}  tau={r.tau:>8.3f}"
              f"{_stars(r.p):<3} se={r.se:>7.3f}  p={r.p:>6.3f}  "
              f"n={int(r.n_left)}/{int(r.n_right)}")
    poly.to_csv(outdir / "07_polynomial_sensitivity.csv", index=False)

    # ---- 8. right-censoring robustness ----
    print("\n" + "-" * 78)
    print(" 8. RIGHT-CENSORING ROBUSTNESS")
    print("-" * 78)
    print(f" {n_censored} observations have an unobservable t+1 outcome (next annual")
    print(" meeting not yet held). Main spec drops them; here they are set to 0,")
    print(" i.e. treated as 'did not refile', which is the conservative reading.")
    cens = sample_all[sample_all.run_var.notna()].copy()
    cens[OUTCOME] = cens[OUTCOME].fillna(0.0)
    cens_res = fit_rd(cens[OUTCOME].to_numpy(float), cens.run_var.to_numpy(float), p=1)
    print(f" censored as 0        : {fmt(cens_res)}")
    print(f" bias-corrected       : {cens_res['tau_bc']:.3f}{_stars(cens_res['p_bc'])} "
          f"({cens_res['se_bc']:.3f})  "
          f"95% CI [{cens_res['ci_lo_bc']:.3f}, {cens_res['ci_hi_bc']:.3f}]")
    print(f" sign vs main spec    : "
          f"{'same' if np.sign(cens_res['tau']) == np.sign(base['tau']) else 'FLIPPED'}")
    pd.DataFrame([cens_res]).to_csv(outdir / "08_censoring_robustness.csv", index=False)

    # ---- 9. markdown summary for the paper ----
    md = [
        "# Stage 2 results",
        "",
        f"RD sample: {len(df)} proposals on their second appearance in five years.",
        f"MSE-optimal bandwidth h* = {h_star:.4f}.",
        "",
        "## Main result",
        "",
        "| Specification | tau | SE | p | 95% CI | n (L/R) |",
        "|---|---|---|---|---|---|",
        f"| Local linear, conventional | {base['tau']:.3f} | {base['se']:.3f} | "
        f"{base['p']:.3f} | [{base['ci_lo']:.3f}, {base['ci_hi']:.3f}] | "
        f"{base['n_left']}/{base['n_right']} |",
        f"| Local linear, bias-corrected | {base['tau_bc']:.3f} | {base['se_bc']:.3f} | "
        f"{base['p_bc']:.3f} | [{base['ci_lo_bc']:.3f}, {base['ci_hi_bc']:.3f}] | "
        f"{base['n_left']}/{base['n_right']} |",
        "",
        "## McCrary density test",
        "",
        f"Statistic {mc['test_stat']:.3f}, p = {mc['p_value']:.3f}. {verdict}.",
        "",
        "## Bandwidth sensitivity",
        "",
        "| h / h* | tau | SE | p | 95% CI | n (L/R) |",
        "|---|---|---|---|---|---|",
    ]
    for _, r in grid.iterrows():
        md.append(f"| {r.multiplier:.2f} | {r.tau:.3f} | {r.se:.3f} | {r.p:.3f} | "
                  f"[{r.ci_lo:.3f}, {r.ci_hi:.3f}] | {int(r.n_left)}/{int(r.n_right)} |")
    md += ["", "## Covariate balance", "",
           "| Covariate | tau | SE | p |", "|---|---|---|---|"]
    for _, r in cb.iterrows():
        md.append(f"| {r.covariate} | {r.tau:.3f} | {r.se:.3f} | {r.p:.3f} |")
    md += ["", "## Placebo cutoffs", "",
           "| Vote share | tau | SE | p |", "|---|---|---|---|"]
    for _, r in pc.iterrows():
        md.append(f"| {r.vote_share:.0%} | {r.tau:.3f} | {r.se:.3f} | {r.p:.3f} |")
    md += ["", "## Right-censoring robustness", "",
           f"{n_censored} observations dropped from the main specification because the "
           "next annual meeting is not yet observable. Setting them to zero:",
           "",
           f"tau = {cens_res['tau']:.3f} (SE {cens_res['se']:.3f}, p {cens_res['p']:.3f}), "
           f"n = {cens_res['n_left']}/{cens_res['n_right']}.", ""]
    (outdir / "results_summary.md").write_text("\n".join(md) + "\n")

    print("\n" + "=" * 78)
    print(f" written to {outdir}/  (8 files)")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
