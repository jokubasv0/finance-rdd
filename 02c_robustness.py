#!/usr/bin/env python3
"""
Stage 2c -- robustness suite for the pooled multi-cutoff RD.

Referee objections this addresses:

  B1  no year fixed effects, and year composition is imbalanced across bars
  B2  no topic fixed effects; topic composition differs sharply by bar
  B6  the 25% bar pools proposals on their 3rd submission with proposals on
      their 65th, which are not the same object
  C1  exact duplicate rows on (cik, filing_date, proposal_desc)

Each check is layered on the baseline so the reader can see what moves the
estimate. The headline is reported as a RANGE across specifications, not as a
single preferred number (objection B3).

Usage:  python 02c_robustness.py [--data rdd_data.csv] [--outdir results]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from rdrobust import rdrobust

OUTCOME = "refiled_t1"
COVARIATES = ["log_assets", "leverage", "roa"]
CLUSTER = "cik"
LEVEL = 95
CUTOFF = 0.0

# Coarse, transparent topic taxonomy. Order matters: first match wins.
TOPIC_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("lobbying_political", ("lobbying", "political", "election", "campaign",
                            "contribution", "partisan")),
    ("climate_environment", ("climate", "emission", "environment", "carbon",
                             "greenhouse", "sustainability", "renewable",
                             "fossil", "biodiversity", "deforestation")),
    ("human_rights_social", ("human right", "racial", "justice", "equity",
                             "diversity", "civil", "slavery", "indigenous",
                             "labor", "workforce", "discriminat", "sexual",
                             "harassment", "gender", "union")),
    ("board_governance", ("board", "director", "chair", "governance",
                          "independent", "special meeting", "written consent",
                          "proxy access", "supermajority", "bylaw", "charter")),
    ("exec_comp", ("compensation", "executive pay", "severance",
                   "golden parachute", "incentive", "say on pay", "equity award")),
    ("health", ("health", "tobacco", "pharmaceutic", "opioid", "vaccine",
                "nutrition", "pandemic")),
    ("animal_welfare", ("animal", "cage", "cruelty", "gestation")),
    ("privacy_tech", ("privacy", "data", "artificial intelligence",
                      "algorithm", "surveillance", "content moderation",
                      "facial recognition")),
    ("charitable", ("charitable", "charity", "giving", "philanthrop")),
    ("antitakeover", ("takeover", "poison pill", "rights plan", "merger",
                      "golden share")),
    ("audit_tax", ("auditor", "tax", "offshore", "shell", "transfer pricing")),
]


def assign_topic(desc: str) -> str:
    """Map a proposal description to one coarse topic bucket."""
    s = str(desc).lower()
    for name, keys in TOPIC_KEYWORDS:
        if any(k in s for k in keys):
            return name
    return "other"


def build(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, de-duplicate, and derive the design columns."""
    before = len(df)
    df = df.drop_duplicates(subset=["cik", "filing_date", "proposal_desc"]).copy()
    df["deduped"] = before - len(df)

    df[OUTCOME] = pd.to_numeric(df[OUTCOME], errors="coerce")
    df = df[df[OUTCOME].notna()].copy()

    n = df["vote_number_5y"]
    df["bar_group"] = np.where(n == 1, 0.05, np.where(n == 2, 0.15, 0.25))
    df["run_var"] = df["vote_share"] - df["bar_group"]
    df["year"] = pd.to_datetime(df["filing_date"]).dt.year
    df["topic"] = df["proposal_desc"].map(assign_topic)
    return df


def dummies(s: pd.Series, drop_first: bool = True) -> np.ndarray:
    """Dummy matrix with a dropped reference level."""
    d = pd.get_dummies(s.astype(str), drop_first=drop_first, dtype=float)
    return d.to_numpy()


def fit(df: pd.DataFrame, year_fe: bool = False, topic_fe: bool = False,
        covs: bool = True, label: str = "") -> dict:
    """Estimate the pooled RD with the requested fixed effects."""
    parts = [
        (df.bar_group == 0.15).astype(float).to_numpy().reshape(-1, 1),
        (df.bar_group == 0.25).astype(float).to_numpy().reshape(-1, 1),
    ]
    if covs:
        for c in COVARIATES:
            parts.append(df[c].astype(float).to_numpy().reshape(-1, 1))
    if year_fe:
        parts.append(dummies(df["year"]))
    if topic_fe:
        parts.append(dummies(df["topic"]))
    X = np.column_stack(parts)

    r = rdrobust(y=df[OUTCOME].to_numpy(float), x=df["run_var"].to_numpy(float),
                 c=CUTOFF, p=1, q=2, bwselect="mserd", vce="nn",
                 level=LEVEL, covs=X, cluster=df[CLUSTER].astype(str).to_numpy())
    return {
        "spec": label, "tau": float(r.coef.iloc[2, 0]), "se": float(r.se.iloc[2, 0]),
        "p": float(r.pv.iloc[2, 0]), "ci_lo": float(r.ci.iloc[2, 0]),
        "ci_hi": float(r.ci.iloc[2, 1]), "h": float(r.bws.iloc[0, 0]),
        "n_left": int(r.N_h[0]), "n_right": int(r.N_h[1]), "n": len(df),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="rdd_data.csv")
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args(argv)

    path = Path(a.data)
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    raw = pd.read_csv(path)
    df = build(raw)
    out = Path(a.outdir)
    out.mkdir(exist_ok=True)

    print("=" * 88)
    print(" STAGE 2c -- ROBUSTNESS SUITE")
    print("=" * 88)
    print(f" rows in : {len(raw)}")
    print(f" duplicates dropped: {int(df.deduped.iloc[0])}")
    print(f" usable  : {len(df)}")
    print(f" firms   : {df[CLUSTER].nunique()}")
    print("\n topic composition by bar:")
    print(pd.crosstab(df.topic, df.bar_group, normalize="columns").round(2).to_string())

    rows = []
    rows.append(fit(df, label="1. baseline (FE + covariates)"))
    rows.append(fit(df, year_fe=True, label="2. + year FE"))
    rows.append(fit(df, topic_fe=True, label="3. + topic FE"))
    rows.append(fit(df, year_fe=True, topic_fe=True, label="4. + year FE + topic FE"))
    rows.append(fit(df, year_fe=True, topic_fe=True, covs=False,
                    label="5. + FE both, no covariates"))

    # 6. 25% bar restricted to third submissions only
    d3 = df[~((df.bar_group == 0.25) & (df.vote_number_5y > 3))]
    rows.append(fit(d3, year_fe=True, topic_fe=True, label="6. 25% bar = 3rd submission only"))

    # 7. drop the 5% bar entirely (lowest-signal group)
    d7 = df[df.bar_group != 0.05]
    rows.append(fit(d7, year_fe=True, topic_fe=True, label="7. drop 5% bar"))

    res = pd.DataFrame(rows)
    print("\n" + "-" * 88)
    print(" ROBUSTNESS TABLE  (bias-corrected, clustered on CIK)")
    print("-" * 88)
    print(f" {'specification':<38}{'tau':>7}{'SE':>7}{'p':>7}{'95% CI':>20}{'n':>7}")
    for _, r in res.iterrows():
        print(f" {r.spec:<38}{r.tau:>7.3f}{r.se:>7.3f}{r.p:>7.3f}"
              f"   [{r.ci_lo:>6.3f},{r.ci_hi:>6.3f}]{int(r.n):>7}")
    res.to_csv(out / "20_robustness_suite.csv", index=False)

    lo, hi = res.tau.min(), res.tau.max()
    print("\n" + "=" * 88)
    print(f" RANGE ACROSS SPECIFICATIONS: tau in [{lo:.3f}, {hi:.3f}]")
    print(f" significant at 5% in {int((res.p < 0.05).sum())} of {len(res)} specifications")
    print(f" positive in {int((res.tau > 0).sum())} of {len(res)}")
    print("=" * 88)

    md = ["# Stage 2c -- robustness suite", "",
          f"Usable observations {len(df)}, {df[CLUSTER].nunique()} firms, "
          f"{int(df.deduped.iloc[0])} duplicates dropped.", "",
          "| Specification | tau | SE | p | 95% CI | n |", "|---|---|---|---|---|---|"]
    for _, r in res.iterrows():
        md.append(f"| {r.spec} | {r.tau:.3f} | {r.se:.3f} | {r.p:.3f} | "
                  f"[{r.ci_lo:.3f}, {r.ci_hi:.3f}] | {int(r.n)} |")
    md += ["", f"Range: tau in [{lo:.3f}, {hi:.3f}]. "
               f"Significant at 5% in {int((res.p < 0.05).sum())}/{len(res)}."]
    (out / "robustness_summary.md").write_text("\n".join(md) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
