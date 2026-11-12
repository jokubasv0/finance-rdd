#!/usr/bin/env python3
"""
Stage 2b -- Multi-cutoff RD pooling all three 14a-8(i)(12) thresholds.

Stage 2 (02_rdd_analysis.py) estimates the 15% discontinuity alone. That sample
is 292 observations with 24 within +/-2pp, giving a minimum detectable effect
near 88pp -- the design cannot see anything realistic.

Rule 14a-8(i)(12) actually imposes THREE bars, all of the same form:

    proposals voted on 1x in 5 years  ->  5%  bar
    proposals voted on 2x in 5 years  ->  15% bar
    proposals voted on 3x or more     ->  25% bar

Each is a resubmission-exclusion rule with the same running variable
(vote_share minus the applicable bar), so they can be stacked. Pooling takes
the sample from 292 to 2,077 and observations within +/-2pp from 24 to 143.

Identification assumption: the effect of becoming eligible for exclusion is
comparable across bars. Threshold fixed effects absorb level differences
between groups; they cannot fix differences in the SLOPE of the effect, which
is why per-threshold estimates are reported alongside the pooled one.

Standard errors are clustered on CIK throughout: the sample has 431 firms and
up to 85 proposals from a single firm, so unclustered SEs would be far too
small.

Usage:  python 02b_multi_cutoff_rd.py [--data rdd_data.csv] [--outdir results]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from rdrobust import rdrobust
from rddensity import rddensity

CUTOFF = 0.0
OUTCOME = "refiled_t1"
COVARIATES = ["log_assets", "leverage", "roa"]
BW_MULTIPLIERS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
PLACEBO_CUTOFFS = [-0.05, 0.05]
LEVEL = 95
CLUSTER = "cik"

GROUPS = [("5% bar (voted once)", 0.05), ("15% bar (voted twice)", 0.15),
          ("25% bar (voted 3+)", 0.25)]


# ---------------------------------------------------------------------------
# sample construction
# ---------------------------------------------------------------------------
def add_group(df: pd.DataFrame) -> pd.DataFrame:
    """Map appearance count to the three legal bars (law caps at 25% for 3+)."""
    n = df["vote_number_5y"]
    df["bar_group"] = np.where(n == 1, 0.05, np.where(n == 2, 0.15, 0.25))
    df["group_label"] = df["bar_group"].map({0.05: GROUPS[0][0],
                                             0.15: GROUPS[1][0],
                                             0.25: GROUPS[2][0]})
    return df


def build_sample(raw: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Usable pooled sample + count of right-censored rows dropped."""
    df = add_group(raw.copy())
    df[OUTCOME] = pd.to_numeric(df[OUTCOME], errors="coerce")
    censored = int(df[df.bar_group.notna()][OUTCOME].isna().sum())
    df = df[df[OUTCOME].notna() & df.run_var.notna()]
    # run_var must be centred on the group's own bar; rebuild defensively.
    df["run_var"] = df["vote_share"] - df["bar_group"]
    return df, censored


def design_matrix(df: pd.DataFrame, with_covariates: bool) -> np.ndarray | None:
    """Threshold dummies always; substantive covariates optionally."""
    cols = [pd.Series((df.bar_group == 0.15).astype(float), index=df.index),
            pd.Series((df.bar_group == 0.25).astype(float), index=df.index)]
    if with_covariates:
        for c in COVARIATES:
            cols.append(df[c].astype(float))
    return np.column_stack(cols)


# ---------------------------------------------------------------------------
# estimation helpers
# ---------------------------------------------------------------------------
def _stars(p: float) -> str:
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def fit(y, x, covs=None, cluster=None, h=None, p=1, c=CUTOFF) -> dict:
    kw = dict(c=c, p=p, q=p + 1, bwselect="mserd", vce="nn", level=LEVEL)
    if covs is not None:
        kw.update(covs=covs)
    if cluster is not None:
        kw.update(cluster=cluster)
    if h is not None:
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


# Minimum detectable effect at 80% power, two-sided 5% test:
# (z_{0.975} + z_{0.80}) * SE = 2.802 * SE. Reported because a coefficient that
# is smaller than its own MDE cannot be distinguished from zero by this design.
MDE_Z = 1.959964 + 0.841621


def mde(r: dict) -> float:
    return MDE_Z * r["se_bc"]


def fmt(r: dict) -> str:
    return (f"{r['tau_bc']:>7.3f}{_stars(r['p_bc']):<3} SE {r['se_bc']:>6.3f}  "
            f"p {r['p_bc']:>5.3f}  95% CI [{r['ci_lo_bc']:>6.3f}, {r['ci_hi_bc']:>6.3f}]  "
            f"n {r['n_left']}/{r['n_right']}  MDE {mde(r):>5.3f}")


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
        print(f"ERROR: {path} not found.", file=sys.stderr)
        return 1

    raw = pd.read_csv(path)
    df, censored = build_sample(raw)
    if len(df) < 100:
        print(f"ERROR: only {len(df)} usable observations.", file=sys.stderr)
        return 1

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    y = df[OUTCOME].to_numpy(float)
    x = df.run_var.to_numpy(float)
    cl = df[CLUSTER].astype(str).to_numpy()

    print("=" * 84)
    print(" STAGE 2b -- MULTI-CUTOFF RD ACROSS ALL THREE 14a-8(i)(12) BARS")
    print("=" * 84)
    print(f" pooled sample          : {len(df)}")
    print(f" dropped, censored      : {censored}")
    print(f" unique firms (clusters): {df[CLUSTER].nunique()}")
    print(f" within +/-2pp          : {(np.abs(x) <= 0.02).sum()}")
    print(f" within +/-5pp          : {(np.abs(x) <= 0.05).sum()}")

    # ---- 1. descriptives by group ----
    rows = []
    for label, _ in GROUPS:
        d = df[df.group_label == label]
        rows.append({"group": label, "n": len(d),
                     "firms": d[CLUSTER].nunique(),
                     "near_2pp": int((d.run_var.abs() <= 0.02).sum()),
                     "refile_rate": d[OUTCOME].mean(),
                     "vote_share": d.vote_share.mean(),
                     "log_assets": d.log_assets.mean(),
                     "leverage": d.leverage.mean(),
                     "roa": d.roa.mean()})
    desc = pd.DataFrame(rows)
    print("\n" + "-" * 84)
    print(" 1. SAMPLE BY THRESHOLD")
    print("-" * 84)
    print(desc.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    desc.to_csv(outdir / "10_pooled_descriptives.csv", index=False)

    # ---- 2. density tests ----
    print("\n" + "-" * 84)
    print(" 2. MCCRARY DENSITY TESTS  (H0: no manipulation)")
    print("-" * 84)
    dens_rows = []
    for label, _ in GROUPS:
        d = df[df.group_label == label]
        r = rddensity(X=d.run_var.to_numpy(), c=CUTOFF)
        stat, pval = float(r.test["t_jk"]), float(r.test["p_jk"])
        dens_rows.append({"sample": label, "test_stat": stat, "p_value": pval,
                          "n": len(d)})
        print(f" {label:<24} t={stat:>6.3f}  p={pval:>6.3f}  n={len(d):>5}  "
              f"{'PASS' if pval > 0.10 else 'FLAG'}")
    r = rddensity(X=x, c=CUTOFF)
    stat, pval = float(r.test["t_jk"]), float(r.test["p_jk"])
    dens_rows.append({"sample": "POOLED", "test_stat": stat, "p_value": pval,
                      "n": len(df)})
    print(f" {'POOLED':<24} t={stat:>6.3f}  p={pval:>6.3f}  n={len(df):>5}  "
          f"{'PASS' if pval > 0.10 else 'FLAG'}")
    dens = pd.DataFrame(dens_rows)
    dens.to_csv(outdir / "11_pooled_density.csv", index=False)

    # ---- 3. pooled specifications ----
    print("\n" + "-" * 84)
    print(" 3. POOLED RD  (threshold FE; SEs clustered on CIK)")
    print("-" * 84)
    fe = design_matrix(df, with_covariates=False)
    fe_cov = design_matrix(df, with_covariates=True)

    specs = {}
    specs["pooled, FE"] = fit(y, x, covs=fe, cluster=cl)
    specs["pooled, FE + covariates"] = fit(y, x, covs=fe_cov, cluster=cl)
    specs["pooled, no adjustment"] = fit(y, x, cluster=cl)
    for name, r in specs.items():
        print(f" {name:<28}{fmt(r)}")

    # ---- 4. per-threshold ----
    print("\n" + "-" * 84)
    print(" 4. PER-THRESHOLD RD  (no pooling; same covariates + clustering)")
    print("-" * 84)
    per_rows = []
    for label, bar in GROUPS:
        d = df[df.group_label == label]
        covs = np.column_stack([d[c].astype(float).to_numpy() for c in COVARIATES])
        r = fit(d[OUTCOME].to_numpy(float), d.run_var.to_numpy(float),
                covs=covs, cluster=d[CLUSTER].astype(str).to_numpy())
        per_rows.append({"group": label, **r})
        print(f" {label:<24}{fmt(r)}")
    per = pd.DataFrame(per_rows)
    per.to_csv(outdir / "12_per_threshold.csv", index=False)

    # The pooled estimate is NOT a weighted average of the per-bar jumps: it
    # imposes one common bandwidth and one common polynomial across groups whose
    # running-variable distributions differ. Report the inverse-variance weighted
    # average alongside it so any contradiction between the two is visible.
    w = 1.0 / per.se_bc.to_numpy(float) ** 2
    wa = float(np.sum(w * per.tau_bc.to_numpy(float)) / np.sum(w))
    wa_se = float(np.sqrt(1.0 / np.sum(w)))
    print(f"\n inverse-variance weighted average of the per-bar jumps: "
          f"{wa:>7.3f} (SE {wa_se:.3f})")
    print(f" -> the pooled estimate should be read against this number, not as an average of it")

    # ---- 5. bandwidth sensitivity, pooled ----
    h_star = specs["pooled, FE"].get("h", 0.08)
    print("\n" + "-" * 84)
    print(" 5. POOLED BANDWIDTH SENSITIVITY")
    print("-" * 84)
    grid = []
    for m in BW_MULTIPLIERS:
        r = fit(y, x, covs=fe, cluster=cl, h=h_star * m)
        grid.append({"multiplier": m, **r})
        print(f" {m:>4.2f}x h*  h={r['h']:.4f}  tau={r['tau']:>7.3f}{_stars(r['p']):<3}"
              f" SE {r['se']:>6.3f}  p {r['p']:>5.3f}  n {r['n_left']}/{r['n_right']}")
    gdf = pd.DataFrame(grid)
    print(f" sign stability: {'stable' if len(set(np.sign(gdf.tau))) == 1 else 'UNSTABLE'}")
    gdf.to_csv(outdir / "13_pooled_bandwidth.csv", index=False)

    # ---- 6. covariate balance, pooled ----
    print("\n" + "-" * 84)
    print(" 6. POOLED COVARIATE BALANCE  (placebo outcomes)")
    print("-" * 84)
    bal = []
    for cov in COVARIATES:
        r = fit(df[cov].to_numpy(float), x, covs=fe, cluster=cl)
        bal.append({"covariate": cov, **r})
        print(f" {cov:<12} tau={r['tau']:>7.3f} SE {r['se']:>6.3f} p {r['p']:>5.3f}"
              f"{'  <-- IMBALANCE' if r['p'] < 0.10 else ''}")
    pd.DataFrame(bal).to_csv(outdir / "14_pooled_balance.csv", index=False)

    # ---- 7. placebo cutoffs, pooled ----
    print("\n" + "-" * 84)
    print(" 7. POOLED PLACEBO CUTOFFS")
    print("-" * 84)
    plc = []
    for c in PLACEBO_CUTOFFS:
        r = fit(y, x, covs=fe, cluster=cl, c=c)
        plc.append({"placebo_offset": c, **r})
        print(f" offset {c:+.2f}  tau={r['tau']:>7.3f} SE {r['se']:>6.3f} p {r['p']:>5.3f}"
              f"{'  <-- unexpected' if r['p'] < 0.10 else ''}")
    pd.DataFrame(plc).to_csv(outdir / "15_pooled_placebo.csv", index=False)

    # ---- 8. polynomial order, pooled ----
    print("\n" + "-" * 84)
    print(" 8. POOLED POLYNOMIAL ORDER")
    print("-" * 84)
    poly = []
    for p in (1, 2):
        r = fit(y, x, covs=fe, cluster=cl, p=p)
        poly.append({"order": p, **r})
        print(f" p={p}  h={r['h']:.4f}  tau={r['tau_bc']:>7.3f}{_stars(r['p_bc']):<3}"
              f" SE {r['se_bc']:>6.3f}  p {r['p_bc']:>5.3f}  n {r['n_left']}/{r['n_right']}")
    pd.DataFrame(poly).to_csv(outdir / "16_pooled_polynomial.csv", index=False)

    # ---- 9. markdown ----
    md = ["# Stage 2b -- pooled multi-cutoff RD", "",
          f"Pooled sample {len(df)} proposals across three thresholds, "
          f"{df[CLUSTER].nunique()} firms, SEs clustered on CIK.", "",
          "## Sample by threshold", "",
          "| Group | n | Firms | near ±2pp | refile rate |",
          "|---|---|---|---|---|"]
    for _, r in desc.iterrows():
        md.append(f"| {r.group} | {int(r.n)} | {int(r.firms)} | {int(r.near_2pp)} | "
                  f"{r.refile_rate:.3f} |")
    md += ["", "## Pooled estimates", "",
           "| Specification | tau | SE | p | 95% CI | n (L/R) | MDE |", "|---|---|---|---|---|---|---|"]
    for name, r in specs.items():
        md.append(f"| {name} | {r['tau_bc']:.3f} | {r['se_bc']:.3f} | {r['p_bc']:.3f} | "
                  f"[{r['ci_lo_bc']:.3f}, {r['ci_hi_bc']:.3f}] | "
                  f"{r['n_left']}/{r['n_right']} | {mde(r):.3f} |")
    md += ["", "## Per-threshold estimates", "",
           "| Group | tau | SE | p | 95% CI | n (L/R) | MDE |", "|---|---|---|---|---|---|---|"]
    for _, r in per.iterrows():
        md.append(f"| {r.group} | {r.tau_bc:.3f} | {r.se_bc:.3f} | {r.p_bc:.3f} | "
                  f"[{r.ci_lo_bc:.3f}, {r.ci_hi_bc:.3f}] | "
                  f"{int(r.n_left)}/{int(r.n_right)} | {mde(r):.3f} |")
    md += ["", f"Inverse-variance weighted average of the per-bar jumps: "
           f"**{wa:.3f}** (SE {wa_se:.3f}). The pooled estimate imposes a common "
           f"bandwidth and polynomial across bars and is not an average of these "
           f"jumps; the two should be read together.", ""]
    md += ["", "## Density tests", "", "| Sample | t | p |", "|---|---|---|"]
    for _, r in dens.iterrows():
        md.append(f"| {r['sample']} | {r['test_stat']:.3f} | {r['p_value']:.3f} |")
    (outdir / "pooled_results_summary.md").write_text("\n".join(md) + "\n")

    print("\n" + "=" * 84)
    print(f" written to {outdir}/ (7 new files)")
    print("=" * 84)
    return 0


if __name__ == "__main__":
    sys.exit(main())
