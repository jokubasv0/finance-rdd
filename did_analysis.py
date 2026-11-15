"""Difference-in-differences around Hungary's April 2026 election.

Panel: eight sovereign 10Y yields, daily, country and date fixed effects.

Estimators reported
  1. Binary DiD, three treatment dates (campaign start, result, inauguration).
  2. Event study in monthly bins relative to April 2026, to expose pre-trends.
  3. Continuous DiD: Hungary's yield on Hungary x P(regime change), P from Polymarket.
  4. Placebo: every country treated in turn, plus randomisation inference.
  5. Leave-one-donor-out and sample-window sensitivity.

Writes out/did_results.txt and out/fig7_event_study.png, out/fig8_placebo_did.png.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from linearmodels.panel import PanelOLS

BASE = Path(__file__).parent
RAW, OUT = BASE / "raw", BASE / "out"

L = []
def p(*a):
    s = " ".join(str(x) for x in a)
    print(s); L.append(s)

def hdr(t):
    p(""); p("=" * 74); p(t); p("=" * 74)

# ------------------------------------------------------------------ data
def inv(name):
    d = json.loads((RAW / f"inv_{name}.json").read_text())
    s = pd.Series({pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize():
                   r["last_closeRaw"] for r in d["data"]}).sort_index()
    return s.apply(pd.to_numeric, errors="coerce").rename(name)

def inv_long(name):
    d = json.loads((RAW / f"long_{name}.json").read_text())
    s = pd.Series({pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize():
                   r["last_closeRaw"] for r in d["data"]}).sort_index()
    return s.apply(pd.to_numeric, errors="coerce").rename(name)

SHORT = ["HU10Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y", "SI10Y", "HR10Y", "AT10Y"]
LONG = ["HU10Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y"]

S = pd.concat([inv(n) for n in SHORT], axis=1, sort=True).ffill(limit=5)
G = pd.concat([inv_long(n) for n in LONG], axis=1, sort=True).ffill(limit=5)

pm = pd.Series({pd.to_datetime(x["t"], unit="s").normalize(): x["p"]
                for x in json.loads((RAW / "pm_orban.json").read_text())["history"]}).sort_index()
S["P"] = (1 - pm).reindex(S.index).ffill()

def to_panel(df, name):
    """Wide country yields -> long MultiIndex (country, date) frame."""
    d = df.copy()
    d.index.name = "date"
    out = d.stack().rename("y").reset_index()
    out["country"] = out["level_1"].str.slice(0, 2)
    out = out.drop(columns="level_1").set_index(["country", "date"]).sort_index()
    out.attrs["name"] = name
    return out

E8 = to_panel(S[SHORT], "8 countries")
E5 = to_panel(G[LONG], "5 countries")

RESULT, INAUG, CAMPAIGN = "2026-04-10", "2026-05-09", "2026-02-27"

def add_dummies(panel, cut, label):
    panel = panel.copy()
    dt = panel.index.get_level_values("date")
    hu = (panel.index.get_level_values("country") == "HU").astype(float)
    post = (dt >= pd.Timestamp(cut)).astype(float)
    panel[label] = hu * post
    return panel

# ------------------------------------------------------------------ 1
hdr("1. SAMPLE")
p(f"8-country panel : {E8.index.get_level_values('date').min().date()} to "
  f"{E8.index.get_level_values('date').max().date()}, "
  f"{len(E8)} country-days, {E8.index.get_level_values('country').nunique()} countries")
p(f"5-country panel : {E5.index.get_level_values('date').min().date()} to "
  f"{E5.index.get_level_values('date').max().date()}, "
  f"{len(E5)} country-days, {E5.index.get_level_values('country').nunique()} countries")
p("")
p("Treatment dates tested: campaign start 2026-02-27, result 2026-04-10, inauguration 2026-05-09. ")
p("Standard errors: Driscoll-Kraay (kernel, bandwidth 10), robust to serial and cross-sectional correlation.")
p("")

# ------------------------------------------------------------------ 2
hdr("2. BINARY DiD: y_it = a_i + l_t + b (HU_i x Post_t) + e_it")

def did(panel, cut, cluster=None, trends=False):
    d = add_dummies(panel.dropna(subset=["y"]), cut, "treat")
    regs = ["treat"]
    if trends:
        t0 = d.index.get_level_values("date").min()
        d["t"] = (d.index.get_level_values("date") - t0).days.astype(float)
        for c in sorted(d.index.get_level_values("country").unique())[1:]:
            d[f"t_{c}"] = d.t * (d.index.get_level_values("country") == c).astype(float)
            regs.append(f"t_{c}")
    mod = PanelOLS(d.y, d[regs], entity_effects=True, time_effects=True, drop_absorbed=True)
    if cluster == "country":
        return mod.fit(cov_type="clustered", cluster_entity=True)
    return mod.fit(cov_type="kernel", kernel="bartlett", bandwidth=10)

def show(res, label):
    b = res.params["treat"]; se = res.std_errors["treat"]; t = res.tstats["treat"]
    pval = res.pvalues["treat"]
    p(f"  {label:34s} b = {b:+7.3f} pp   se {se:.3f}   t {t:+6.2f}   p {pval:.3f}   N {int(res.nobs)}")
    return b, se, t, pval

rows = []
for cut, lab in [(RESULT, "result (10 Apr 2026)"),
                 (CAMPAIGN, "campaign (27 Feb 2026)"),
                 (INAUG, "inauguration (9 May 2026)")]:
    p(f"{lab}, 8-country panel, 2025-06 to 2026-11")
    show(did(E8, cut), "no trends, DK")
    show(did(E8, cut, trends=True), "country trends, DK")
    show(did(E8, cut, cluster="country"), "no trends, cluster(8)")
    p("")

p("Same, 5-country panel, 2022-01 to 2026-11 (long pre-period)")
for cut, lab in [(RESULT, "result (10 Apr 2026)"), (CAMPAIGN, "campaign (27 Feb 2026)")]:
    show(did(E5, cut), "no trends, DK")
    show(did(E5, cut, trends=True), "country trends, DK")
    show(did(E5, cut, cluster="country"), "no trends, cluster(5)")
p("")

# ------------------------------------------------------------------ 3
hdr("3. EVENT STUDY, MONTHLY BINS RELATIVE TO APRIL 2026")
ev = E8.dropna(subset=["y"]).copy()
ev = ev.reset_index()
ev["m"] = (ev.date.dt.year - 2026) * 12 + ev.date.dt.month - 4
ev["hu"] = (ev.country == "HU").astype(float)
# bins: <=-6, -5..-2, -1, 0, +1, +2..+7
def binof(m):
    if m <= -2: return m          # every pre-treatment month gets its own lead
    if m == -1: return -1
    if m == 0: return 0
    if m == 1: return 1
    return 2                      # June 2026 onward pooled
ev["bin"] = ev.m.apply(binof)
ev = ev.dropna(subset=["bin"])
ev["bin"] = ev.bin.astype(int)
# base period: -2 (February 2026, before the campaign)
base = -2
dums = []
for b in sorted(ev.bin.unique()):
    if b == base:
        continue
    col = f"d{b}"
    ev[col] = ev.hu * (ev.bin == b).astype(float)
    dums.append(col)
ev = ev.set_index(["country", "date"])
mod = PanelOLS(ev.y, ev[dums], entity_effects=True, time_effects=True, drop_absorbed=True)
res = mod.fit(cov_type="kernel", kernel="bartlett", bandwidth=10)
p(f"Base month: February 2026 (m = {base}). Coefficients are percentage points.")
p(f"{'month':10s} {'rel':>4s} {'coef':>8s} {'se':>7s} {'t':>7s}")
NAMES = {-10: "Jun 25", -9: "Jul", -8: "Aug", -7: "Sep", -6: "Oct",
         -5: "Nov", -4: "Dec", -3: "Jan 26", -2: "Feb", -1: "Mar",
         0: "Apr", 1: "May", 2: "Jun+"}
for b in sorted(ev.bin.unique()):
    if b == base:
        p(f"{NAMES[b]:10s} {b:+4d} {0.0:+8.3f} {'base':>7s} {'':>7s}")
        continue
    col = f"d{b}"
    p(f"{NAMES[b]:10s} {b:+4d} {res.params[col]:+8.3f} {res.std_errors[col]:7.3f} {res.tstats[col]:+7.2f}")

pre = [f"d{b}" for b in sorted(ev.bin.unique()) if b < base]
if pre:
    R = np.zeros((len(pre), len(res.params)))
    for i, c in enumerate(pre):
        R[i, list(res.params.index).index(c)] = 1.0
    w = res.wald_test(restriction=R, value=np.zeros(len(pre)))
    p("")
    p(f"Joint test that all pre-treatment leads (Oct 2025 - Jan 2026) are zero: "
      f"chi2 = {w.stat:.2f}, p = {w.pval:.3f}")

# figure
fig, ax = plt.subplots(figsize=(8.2, 4.4))
xs, ys, lo, hi = [], [], [], []
for b in sorted(ev.bin.unique()):
    if b == base:
        xs.append(b); ys.append(0.0); lo.append(0.0); hi.append(0.0)
        continue
    col = f"d{b}"
    xs.append(b); ys.append(res.params[col])
    lo.append(res.params[col] - 1.96 * res.std_errors[col])
    hi.append(res.params[col] + 1.96 * res.std_errors[col])
ax.axhline(0, color="black", lw=0.8)
ax.axvline(-0.5, color="#c00000", lw=0.9, ls=":")
ax.errorbar(xs, ys, yerr=[np.array(ys) - np.array(lo), np.array(hi) - np.array(ys)],
            fmt="o-", color="#1f4e79", lw=1.6, ms=5, capsize=3)
ax.set_xticks(xs)
ax.set_xticklabels([NAMES[b] for b in xs], fontsize=7.5)
ax.set_ylabel("Hungary minus donors, pp")
ax.set_title("Event study: monthly difference-in-differences, base February 2026")
ax.annotate("election", (0, ax.get_ylim()[1]*0.92), fontsize=8, ha="center", color="#c00000")
fig.tight_layout(); fig.savefig(OUT / "fig7_event_study.png", dpi=170); plt.close(fig)

# ------------------------------------------------------------------ 4
hdr("4. CONTINUOUS DiD: y_it = a_i + l_t + b (HU_i x P_t) + e_it")
p("P is the Polymarket probability that Orban does not remain PM, carried forward between prints.")
p("Window 2025-07-25 to 2026-05-08, 8-country panel.")
cont = E8.dropna(subset=["y"]).copy()
dt = cont.index.get_level_values("date")
hu = (cont.index.get_level_values("country") == "HU").astype(float)
Pw = S.P.reindex(dt).values
cont["huP"] = hu * Pw
cont = cont.loc[(dt >= "2025-07-25") & (dt <= "2026-05-08")]
cont = cont.dropna(subset=["huP"])
for cov, lab in [("kernel", "Driscoll-Kraay"), ("clustered", "clustered by country (8)")]:
    m = PanelOLS(cont.y, cont[["huP"]], entity_effects=True, time_effects=True, drop_absorbed=True)
    kw = dict(cov_type="kernel", kernel="bartlett", bandwidth=10) if cov == "kernel" \
         else dict(cov_type="clustered", cluster_entity=True)
    r = m.fit(**kw)
    p(f"  {lab:26s} b = {r.params['huP']:+8.3f} pp per unit P   "
      f"se {r.std_errors['huP']:.3f}   t {r.tstats['huP']:+6.2f}   N {int(r.nobs)}")
p("")
p("A coefficient of -1.0 means: going from P = 0 to P = 1 lowers Hungary's yield by 1 pp")
p("relative to its donors, i.e. a full repricing of regime change is worth 100 bp.")

# ------------------------------------------------------------------ 5
hdr("5. PLACEBO TREATED UNITS AND RANDOMISATION INFERENCE")
p("Each country is treated in turn, result date 2026-04-10, same panel and specification.")
placebo = {}
for c in sorted(E8.reset_index().country.unique()):
    d = E8.dropna(subset=["y"]).copy()
    dt = d.index.get_level_values("date")
    ind = (d.index.get_level_values("country") == c).astype(float)
    d["treat"] = ind * (dt >= pd.Timestamp(RESULT)).astype(float)
    m = PanelOLS(d.y, d[["treat"]], entity_effects=True, time_effects=True, drop_absorbed=True)
    r = m.fit(cov_type="kernel", kernel="bartlett", bandwidth=10)
    placebo[c] = r.params["treat"]
    p(f"  {c:4s} b = {r.params['treat']:+7.3f} pp   se {r.std_errors['treat']:.3f}   "
      f"t {r.tstats['treat']:+6.2f}   p {r.pvalues['treat']:.3f}")
hu_b = placebo["HU"]
rank = 1 + sum(v < hu_b for k, v in placebo.items() if k != "HU")
p("")
p(f"Hungary ranks {rank} of {len(placebo)} (more negative = lower yield).")
p(f"Randomisation-inference p-value: {sum(v <= hu_b for v in placebo.values())/len(placebo):.3f}")
p(f"With {len(placebo)} units the smallest attainable p-value is {1/len(placebo):.3f}.")

fig, ax = plt.subplots(figsize=(7.0, 4.0))
ks = list(placebo.keys()); vs = [placebo[k] for k in ks]
cols = ["#c00000" if k == "HU" else "#1f4e79" for k in ks]
ax.bar(ks, vs, color=cols)
ax.axhline(0, color="black", lw=0.8)
ax.set_ylabel("DiD coefficient, pp")
ax.set_title("Placebo treatment: each country in turn")
fig.tight_layout(); fig.savefig(OUT / "fig8_placebo_did.png", dpi=170); plt.close(fig)

# ------------------------------------------------------------------ 6
hdr("6. LEAVE-ONE-DONOR-OUT, 8-country panel, result date")
for drop in [x for x in SHORT if x != "HU10Y"]:
    keep = [x for x in SHORT if x != drop]
    d = S[keep].ffill(limit=5)
    d["P"] = S.P
    pan = to_panel(d[keep], "x").dropna(subset=["y"])
    dt = pan.index.get_level_values("date")
    hu = (pan.index.get_level_values("country") == "HU").astype(float)
    pan["treat"] = hu * (dt >= pd.Timestamp(RESULT)).astype(float)
    m = PanelOLS(pan.y, pan[["treat"]], entity_effects=True, time_effects=True, drop_absorbed=True)
    r = m.fit(cov_type="kernel", kernel="bartlett", bandwidth=10)
    p(f"  drop {drop[:2]:4s} b = {r.params['treat']:+7.3f} pp   se {r.std_errors['treat']:.3f}   "
      f"t {r.tstats['treat']:+6.2f}")

# ------------------------------------------------------------------ 7
hdr("7. WINDOW SENSITIVITY, 8-country panel, result date")
for a, b in [("2025-06-01", "2026-11-13"), ("2025-07-25", "2026-05-08"),
             ("2025-10-01", "2026-11-13"), ("2026-01-01", "2026-11-13"),
             ("2025-06-01", "2026-06-30")]:
    d = S[SHORT].copy()
    d = d.loc[a:b].ffill(limit=5)
    pan = to_panel(d, "x").dropna(subset=["y"])
    dt = pan.index.get_level_values("date")
    hu = (pan.index.get_level_values("country") == "HU").astype(float)
    pan["treat"] = hu * (dt >= pd.Timestamp(RESULT)).astype(float)
    m = PanelOLS(pan.y, pan[["treat"]], entity_effects=True, time_effects=True, drop_absorbed=True)
    r = m.fit(cov_type="kernel", kernel="bartlett", bandwidth=10)
    p(f"  {a} to {b}  b = {r.params['treat']:+7.3f} pp   se {r.std_errors['treat']:.3f}   "
      f"t {r.tstats['treat']:+6.2f}   N {int(r.nobs)}")

(OUT / "did_results.txt").write_text("\n".join(L))
p("")
p(f"written to {OUT / 'did_results.txt'}")
