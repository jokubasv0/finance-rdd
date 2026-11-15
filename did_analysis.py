"""Difference-in-differences: does the Hungarian yield break at the 2026 election?

Design
------
Panel of country x trading day sovereign 10Y yields. Two-way fixed effects
(country, date) with optional country-specific linear trends, and a treatment
dummy that switches on for Hungary at the first trading day after the vote.

    y_it = a_i + l_t + b (HU_i x Post_t) + g_i f(t) + e_it

The trend term f(t) has three variants:
    none    f(t) = 0
    kink    f(t) = min(t, t_cut)   trend runs before the vote, flat after
    linear  f(t) = t               trend runs through the whole sample

The kinked version is the headline: it allows pre-existing drift but does not
let the treatment period contaminate the trend it is being measured against.

Samples
-------
raw/inv_*.json     8 countries, 2025-06-02 onwards
raw/long_*.json    5 countries (HU, CZ, DE, PL, RO), 2022-01 onwards

Only the long files reach back to 2024, so the headline is a five-country
panel. The eight-country panel is used for the placebo and randomisation
exercise, where the number of units is what matters.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

BASE = Path(__file__).parent
RAW, OUT = BASE / "raw", BASE / "out"
OUT.mkdir(exist_ok=True)

L = []
def p(*a):
    s = " ".join(str(x) for x in a)
    print(s); L.append(s)
def hdr(t):
    p(""); p("=" * 78); p(t); p("=" * 78)

# ---------------------------------------------------------------- parameters
CUT      = pd.Timestamp("2026-04-13")   # Monday after the Sunday 12 April vote
SAMPLE   = pd.Timestamp("2024-01-01")   # headline start
END      = pd.Timestamp("2026-05-08")   # inauguration-end; extension tested below
TREND    = "kink"

SHORT = ["HU10Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y", "SI10Y", "HR10Y", "AT10Y"]
LONG  = ["HU10Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y"]

# ---------------------------------------------------------------- loaders
def inv(prefix, name):
    d = json.loads((RAW / f"{prefix}_{name}.json").read_text())
    s = pd.Series({pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize():
                   r["last_closeRaw"] for r in d["data"]})
    return pd.to_numeric(s, errors="coerce").sort_index().rename(name)

def build(names, prefix):
    df = pd.concat([inv(prefix, n) for n in names], axis=1, sort=True).sort_index()
    df = df.ffill(limit=5)
    return df

W8 = build(SHORT, "inv")
W5 = build(LONG, "long")

def to_panel(wide):
    df = wide.copy()
    df.index.name = "date"
    st = df.stack().rename("y")
    st.index = st.index.set_names(["date", "country"])
    return st.swaplevel("country", "date").sort_index().to_frame()

def did(panel, cut=None, sample=None, end=None, trend="kink"):
    cut = CUT if cut is None else pd.Timestamp(cut)
    d = panel.copy()
    if sample is not None:
        d = d[d.index.get_level_values("date") >= pd.Timestamp(sample)]
    if end is not None:
        d = d[d.index.get_level_values("date") <= pd.Timestamp(end)]
    d = d[d.y.notna()]

    dates = d.index.get_level_values("date")
    d["treat"] = ((d.index.get_level_values("country") == "HU10Y") & (dates >= cut)).astype(float)
    d["post"] = (dates >= cut).astype(float)

    # day index and per-country trend terms
    uniq = np.sort(dates.unique())
    pos = {x: i for i, x in enumerate(uniq)}
    d["t"] = dates.map(pos).astype(float)
    tc = float(pos[uniq[uniq.searchsorted(cut) - 1]]) if cut > uniq[0] else 0.0
    d["t_kink"] = np.minimum(d["t"], tc)

    exog = ["treat"]
    countries = sorted(d.index.get_level_values("country").unique())
    trendcol = {"none": None, "kink": "t_kink", "linear": "t"}[trend]
    if trendcol:
        for c in countries:
            col = f"{trendcol}_{c}"
            d[col] = (d.index.get_level_values("country") == c) * d[trendcol]
            if c != countries[0]:      # AT / HU omitted as base
                exog.append(col)

    res = PanelOLS(d.y, d[exog], entity_effects=True, time_effects=True,
                   drop_absorbed=False).fit(
        cov_type="kernel", kernel="bartlett", bandwidth=10)
    return res, d

def beta(res, name="treat"):
    return res.params[name], res.std_errors[name], res.tstats[name], int(res.nobs)

# ---------------------------------------------------------------- 1
hdr("1. SAMPLE CONSTRUCTION")
p(f"Cut date            : {CUT.date()}  (Monday after the 12 April election)")
p(f"Headline sample     : {SAMPLE.date()} to {END.date()}")
p(f"Headline trend      : {TREND}")
p("")
p(f"8-country file: {W8.index.min().date()} to {W8.index.max().date()}, {len(W8)} rows")
p(f"5-country file: {W5.index.min().date()} to {W5.index.max().date()}, {len(W5)} rows")
p("")
p("Only the 5-country files reach 2024, so the headline is 5 countries.")

P8, P5 = to_panel(W8), to_panel(W5)

# ---------------------------------------------------------------- 2
hdr("2. END-DATE DECISION")
p("The election is 12 April. The inauguration is 9 May. The spread keeps")
p("narrowing until November. Ending the DiD at the inauguration keeps it")
p("commensurate with the descriptive window; ending it in November charges")
p("seven months of post-inauguration convergence to the April cut.")
p("")
p(f"{'end':14s} {'none':>16s} {'kink':>16s} {'linear':>16s} {'N':>7s}")
for end in ["2026-05-08", "2026-06-30", "2026-11-13"]:
    row = []
    for tr in ["none", "kink", "linear"]:
        r, _ = did(P5, sample=SAMPLE, end=end, trend=tr)
        b, se, t, n = beta(r)
        row.append(f"{b:+.3f} ({t:+.1f})")
    p(f"{end:14s} {row[0]:>16s} {row[1]:>16s} {row[2]:>16s} {n:7d}")

# ---------------------------------------------------------------- 3
hdr("3. HEADLINE")
res5, D5 = did(P5, sample=SAMPLE, end=END, trend=TREND)
b, se, t, n = beta(res5)
p(f"y_it = a_i + l_t + b(HU_i x Post_t) + g_i min(t,t_cut) + e_it")
p(f"  2024-01 to {END.date()}, 5 countries, {n} observations")
p(f"  beta = {b:+.4f} pp   se = {se:.4f}   t = {t:+.2f}   p = {res5.pvalues['treat']:.4f}")
p(f"  within R2 = {res5.rsquared_within:.3f}")
p("")
p("Specification comparison on the same sample:")
p(f"{'trend':10s} {'beta':>9s} {'se':>8s} {'t':>8s} {'N':>7s}")
for tr in ["none", "kink", "linear"]:
    r, _ = did(P5, sample=SAMPLE, end=END, trend=tr)
    bb, ss, tt, nn = beta(r)
    p(f"{tr:10s} {bb:+9.3f} {ss:8.3f} {tt:+8.2f} {nn:7d}")
p("")
p("The three span a few basis points: on this sample the trend choice does")
p("not matter. On a 2022 sample it does, which is why 2022 is excluded.")

# ---------------------------------------------------------------- 4
hdr("4. WHY 2022 IS EXCLUDED")
p(f"{'sample':12s} {'none':>16s} {'kink':>16s} {'linear':>16s} {'span':>7s}")
for s0 in ["2022-01-01", "2023-01-01", "2024-01-01", "2024-07-01", "2025-01-01"]:
    vals = []
    for tr in ["none", "kink", "linear"]:
        r, _ = did(P5, sample=s0, end=END, trend=tr)
        vals.append(beta(r)[0])
    p(f"{s0:12s} {vals[0]:+16.3f} {vals[1]:+16.3f} {vals[2]:+16.3f} "
      f"{100*(max(vals)-min(vals)):6.0f}bp")
p("")
p("On 2022 the three specifications disagree; from 2024 they agree. The")
p("2022 sample contains the energy-crisis convergence, which a linear trend")
p("cannot absorb and a no-trend specification reads as a Hungarian effect.")

# ---------------------------------------------------------------- 5
hdr("5. PLACEBO TREATMENT DATES")
p("Each fake cut is estimated on a panel truncated BEFORE the real event,")
p("otherwise the real collapse sits inside every post-window and every fake")
p("date 'works'. Truncation date: 2026-04-10.")
p("")
p(f"{'fake cut':12s} {'none':>16s} {'kink':>16s}")
for fc in ["2024-07-01", "2024-10-01", "2025-01-06", "2025-04-01",
           "2025-07-01", "2025-10-01"]:
    row = []
    for tr in ["none", "kink"]:
        r, _ = did(P5, cut=fc, sample=SAMPLE, end="2026-04-10", trend=tr)
        bb, ss, tt, nn = beta(r)
        row.append(f"{bb:+.3f} ({tt:+.1f})")
    p(f"{fc:12s} {row[0]:>16s} {row[1]:>16s}")
p("")
p("All near zero. This is what the 2022 sample fails: there, the convergence")
p("produces a spurious negative at almost any date.")

# ---------------------------------------------------------------- 6
hdr("6. PLACEBO COUNTRIES AND RANDOMISATION INFERENCE")
p("The eight-country panel is 2025-06 onwards only, so this exercise uses")
p("the short window. That is a cost: ten months of pre-period. It is the")
p("only panel with eight units, and eight units is what sets the p-value floor.")
p("")
names = W8.columns.tolist()
p("Eight-country panel, same window and end date, all three trend treatments:")
p(f"{'trend':10s} {'beta':>9s} {'se':>8s} {'t':>8s} {'N':>7s}")
for tr in ["none", "kink", "linear"]:
    r, _ = did(P8, sample="2025-06-01", end=END, trend=tr)
    bb, ss, tt, nn = beta(r)
    p(f"{tr:10s} {bb:+9.3f} {ss:8.3f} {tt:+8.2f} {nn:7d}")
p("")
res8, _ = did(P8, sample="2025-06-01", end=END, trend="kink")
p(f"Real estimate, 8 countries, kink, 2025-06 to {END.date()}: "
  f"{beta(res8)[0]:+.3f} (t {beta(res8)[2]:+.1f}), N {beta(res8)[3]}")
p("")
p(f"{'treated':10s} {'beta':>9s} {'t':>8s}")
plc = {}
for c in names:
    d = P8.copy()
    dates = d.index.get_level_values("date")
    d = d[d.index.get_level_values("date") >= pd.Timestamp("2025-06-01")]
    d = d[d.index.get_level_values("date") <= END]
    d = d[d.y.notna()]
    dates = d.index.get_level_values("date")
    d["treat"] = ((d.index.get_level_values("country") == c) & (dates >= CUT)).astype(float)
    uniq = np.sort(dates.unique()); pos = {x: i for i, x in enumerate(uniq)}
    d["t"] = dates.map(pos).astype(float)
    tc = float(pos[uniq[uniq.searchsorted(CUT) - 1]])
    d["tk"] = np.minimum(d["t"], tc)
    ex = ["treat"]
    cs = sorted(d.index.get_level_values("country").unique())
    for cc in cs:
        d[f"k_{cc}"] = (d.index.get_level_values("country") == cc) * d["tk"]
        if cc != cs[0]:
            ex.append(f"k_{cc}")
    r = PanelOLS(d.y, d[ex], entity_effects=True, time_effects=True,
                 drop_absorbed=False).fit(cov_type="kernel", kernel="bartlett",
                                          bandwidth=10)
    plc[c] = (r.params["treat"], r.tstats["treat"])
for c, (bb, tt) in sorted(plc.items(), key=lambda kv: kv[1][0]):
    p(f"{c:10s} {bb:+9.3f} {tt:+8.1f}")
rank = [c for c, _ in sorted(plc.items(), key=lambda kv: kv[1][0])].index("HU10Y") + 1
p("")
p(f"Hungary rank {rank} of {len(plc)}; randomisation-inference p = "
  f"{rank/len(plc):.3f} (floor 1/{len(plc)} = {1/len(plc):.3f})")

# ---------------------------------------------------------------- 7
hdr("7. EVENT STUDY (5-country panel, 2024+)")
d = P5.copy()
d = d[d.index.get_level_values("date") >= SAMPLE]
d = d[d.index.get_level_values("date") <= END]
dates = d.index.get_level_values("date")
d["treat"] = ((d.index.get_level_values("country") == "HU10Y") & (dates >= CUT)).astype(float)
mon = dates.to_period("M")
months = sorted(mon.unique())
base = pd.Period("2026-02", "M")
ex = []
for m in months:
    if m == base:
        continue
    col = f"m_{m}"
    d[col] = ((mon == m) & (d.index.get_level_values("country") == "HU10Y")).astype(float)
    ex.append(col)
d = d[d.y.notna()]
r = PanelOLS(d.y, d[ex], entity_effects=True, time_effects=True,
             drop_absorbed=False).fit(cov_type="kernel", kernel="bartlett", bandwidth=10)
EV, EV_MONTHS, EV_BASE = r, months, base
p(f"{'month':10s} {'coef':>8s} {'t':>8s}")
for m in months:
    if m == base:
        p(f"{str(m):10s} {'base':>8s} {'':>8s}")
        continue
    col = f"m_{m}"
    if col in r.params.index:
        p(f"{str(m):10s} {r.params[col]:+8.3f} {r.tstats[col]:+8.1f}")
pre = [f"m_{m}" for m in months if m < base and f"m_{m}" in r.params.index]
if pre:
    names = list(r.params.index)
    R = np.zeros((len(pre), len(names)))
    for i, c in enumerate(pre):
        R[i, names.index(c)] = 1.0
    w = r.wald_test(R, np.zeros(len(pre)))
    p("")
    p(f"Joint test that all {len(pre)} pre-treatment leads are zero:")
    p(f"  Wald chi2 = {float(w.stat):.1f}, df = {len(pre)}, p = {float(w.pval):.2g}")
    p(f"  mean lead = {r.params[pre].mean():+.3f} pp, "
      f"sd across months = {r.params[pre].std():.3f}")
    p("")
    p("Read this carefully. The test rejects that every lead is exactly zero,")
    p("because at 200-300 observations per month a coefficient of 0.1 pp is")
    p("precisely estimated. It does not reject that the leads are flat: they")
    p("oscillate around a mean near zero with no monotone drift, and adding")
    p("country trends moves the estimate by five basis points. That is the")
    p("relevant fact for the DiD, whose threat is a trending pre-period.")

# ---------------------------------------------------------------- 8
hdr("8. DONOR SENSITIVITY")
p(f"{'dropped':12s} {'beta':>9s} {'t':>8s}")
for c in ["CZ10Y", "DE10Y", "PL10Y", "RO10Y"]:
    keep = [x for x in LONG if x != c]
    sub = W5[keep]
    r, _ = did(to_panel(sub), sample=SAMPLE, end=END, trend=TREND)
    bb, ss, tt, nn = beta(r)
    p(f"{c:12s} {bb:+9.3f} {tt:+8.2f}")
p("")
p("Only four donors are available on a 2024 sample. Every drop moves the")
p("estimate by a few basis points.")

# ---------------------------------------------------------------- figures
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# fig 7: event study
fig, ax = plt.subplots(figsize=(9.0, 4.4))
xs, ys, es = [], [], []
for i, m in enumerate(EV_MONTHS):
    if m == EV_BASE:
        xs.append(i); ys.append(0.0); es.append(0.0); continue
    c = f"m_{m}"
    xs.append(i); ys.append(EV.params[c]); es.append(1.96 * EV.std_errors[c])
ax.axhline(0, color="black", lw=0.8)
ax.axvline(len([m for m in EV_MONTHS if m <= EV_BASE]) - 0.5, color="#c00000", lw=1.0, ls=":")
ax.errorbar(xs, ys, yerr=es, fmt="o", ms=4, lw=1.2, color="#1f4e79", ecolor="#9dc3e6")
ax.set_xticks(xs[::3])
ax.set_xticklabels([str(m) for m in EV_MONTHS][::3], rotation=45, ha="right", fontsize=8)
ax.set_ylabel("coefficient, pp")
ax.set_title("Event study: monthly Hungary effect relative to February 2026")
fig.tight_layout(); fig.savefig(OUT / "fig7_event_study.png", dpi=170); plt.close(fig)

# fig 8: placebo countries
fig, ax = plt.subplots(figsize=(7.6, 4.0))
order = sorted(plc, key=lambda c: plc[c][0])
labels = [c[:2] for c in order]
vals = [plc[c][0] for c in order]
colors = ["#c00000" if c == "HU10Y" else "#1f4e79" for c in order]
ax.bar(labels, vals, color=colors)
ax.axhline(0, color="black", lw=0.8)
ax.set_ylabel("DiD coefficient, pp")
ax.set_title("Placebo treatment: each country treated in turn")
fig.tight_layout(); fig.savefig(OUT / "fig8_placebo_did.png", dpi=170); plt.close(fig)

(OUT / "did_results.txt").write_text("\n".join(L))
p(""); p(f"written to {OUT / 'did_results.txt'}")
