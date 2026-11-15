"""Analysis: Hungarian sovereign risk and the market-implied probability of regime change.

Outputs (out/):
  results.txt
  fig1_prob_vs_spread.png
  fig2_monthly_scatter.png
  fig3_market_model.png
"""
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).parent
RAW = BASE / "raw"
OUT = BASE / "out"
OUT.mkdir(exist_ok=True)

L = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    L.append(s)


def hdr(t):
    p("")
    p("=" * 78)
    p(t)
    p("=" * 78)


# ------------------------------------------------------------------ data
def load_inv(prefix, name):
    d = json.loads((RAW / f"{prefix}_{name}.json").read_text())
    rows = {
        pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize(): r["last_closeRaw"]
        for r in d["data"]
    }
    return pd.Series(rows).sort_index().rename(name)


def load_yh(prefix, name):
    d = json.loads((RAW / f"{prefix}_{name}.json").read_text())["chart"]["result"][0]
    ts = pd.to_datetime(d["timestamp"], unit="s").normalize()
    return pd.Series(d["indicators"]["quote"][0]["close"], index=ts).dropna().rename(name)


short = pd.concat(
    [load_inv("inv", n) for n in ["HU10Y", "HU5Y", "CZ10Y", "DE10Y", "PL10Y",
                                  "RO10Y", "CZ2Y", "DE2Y", "SI10Y", "HR10Y", "AT10Y"]]
    + [load_yh("yh", n) for n in ["US10Y", "VIX", "BRENT", "USDHUF"]],
    axis=1, sort=True,
)
pm = json.loads((RAW / "pm_orban.json").read_text())["history"]
pm = pd.Series({pd.to_datetime(x["t"], unit="s").normalize(): x["p"] for x in pm}).sort_index()
short["orban"] = pm
short["P"] = 1 - short["orban"]

long = pd.concat(
    [load_inv("long", n) for n in ["HU10Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y"]]
    + [load_yh("long_yh", n) for n in ["US10Y", "VIX", "BRENT"]],
    axis=1, sort=True,
)

# ------------------------------------------------------------------ sample
S0, S1 = "2025-07-25", "2026-05-09"       # Polymarket market life
short = short.apply(pd.to_numeric, errors="coerce")
long = long.apply(pd.to_numeric, errors="coerce")
d = short.loc[S0:S1].copy()
d["P"] = d["P"].ffill()
d["S_HUCZ"] = d["HU10Y"] - d["CZ10Y"]
d["S_HUDE"] = d["HU10Y"] - d["DE10Y"]
d["lnBrent"] = np.log(d["BRENT"])
d = d.dropna(subset=["HU10Y", "CZ10Y", "P"])

hdr("1. SAMPLE AND HEADLINE NUMBERS")
p(f"Window: {d.index.min().date()} to {d.index.max().date()}   N trading days = {len(d)}")
p(f"Polymarket P(Orban does not remain PM): {d.P.iloc[0]:.3f} -> {d.P.iloc[-1]:.3f}")
p(f"HU 10Y:      {d.HU10Y.iloc[0]:.2f}% -> {d.HU10Y.iloc[-1]:.2f}%  "
  f"({100*(d.HU10Y.iloc[-1]-d.HU10Y.iloc[0]):+.0f} bp)")
p(f"CZ 10Y:      {d.CZ10Y.iloc[0]:.2f}% -> {d.CZ10Y.iloc[-1]:.2f}%  "
  f"({100*(d.CZ10Y.iloc[-1]-d.CZ10Y.iloc[0]):+.0f} bp)")
p(f"HU-CZ spread:{d.S_HUCZ.iloc[0]:.2f}pp -> {d.S_HUCZ.iloc[-1]:.2f}pp "
  f"({100*(d.S_HUCZ.iloc[-1]-d.S_HUCZ.iloc[0]):+.0f} bp)")
p(f"HU 5Y:       {d.HU5Y.iloc[0]:.2f}% -> {d.HU5Y.iloc[-1]:.2f}%  "
  f"({100*(d.HU5Y.iloc[-1]-d.HU5Y.iloc[0]):+.0f} bp)")
p(f"USDHUF:      {d.USDHUF.dropna().iloc[0]:.1f} -> {d.USDHUF.dropna().iloc[-1]:.1f}")

# how stale is the Polymarket series?
upd_days = (d.P.diff() != 0).sum()
hdr("2. DATA QUALITY OF THE PREDICTION MARKET SERIES")
p(f"Trading days with a non-zero change in P: {upd_days} of {len(d)-1} "
  f"({100*upd_days/(len(d)-1):.0f}%)")
p(f"Largest single-day change: {100*d.P.diff().abs().max():.1f} pp on "
  f"{d.P.diff().abs().idxmax().date()}")
p("Polymarket daily candles only record days with trades. Long flat stretches mean")
p("stale prices, not unchanged beliefs. The market also stopped trading 9-22 April:")
p(d.loc["2026-04-07":"2026-04-24", ["orban", "HU10Y", "CZ10Y"]].round(3).to_string())

# ------------------------------------------------------------------ event windows
hdr("3. EVENT WINDOWS (raw changes, bp)")
def win(a, b, label):
    s = d.loc[a:b, "S_HUCZ"]; h = d.loc[a:b, "HU10Y"]; q = d.loc[a:b, "P"]
    p(f"{label:26s} HU-CZ {100*(s.iloc[-1]-s.iloc[0]):+7.0f} bp | "
      f"HU10Y {100*(h.iloc[-1]-h.iloc[0]):+7.0f} bp | "
      f"P {q.iloc[0]:.3f}->{q.iloc[-1]:.3f}")

win("2025-07-25", "2026-02-27", "Jul-25 to Feb-26")
win("2026-02-27", "2026-04-09", "poll shift to vote")
win("2025-07-25", "2026-04-09", "full pre-election")
win("2026-04-09", "2026-04-30", "vote to end-April")
win("2026-04-09", "2026-05-08", "vote to inauguration")
p("")
p("After the prediction market resolves (descriptive only, no P available):")
full = short.apply(pd.to_numeric, errors="coerce")
full["S"] = full.HU10Y - full.CZ10Y
for a, b, lab in [("2026-05-08", "2026-11-13", "inauguration to Nov-26")]:
    s = full.loc[a:b, "S"].dropna()
    p(f"  {lab:26s} HU-CZ {100*(s.iloc[-1]-s.iloc[0]):+7.0f} bp")
p("")
p("Slope check: bp of spread per 100 pp of P, across disjoint windows")
for a, b, lab in [("2025-07-25", "2026-02-27", "Jul-25 to Feb-26"),
                  ("2026-02-27", "2026-04-09", "poll shift to vote"),
                  ("2026-04-09", "2026-05-08", "vote to inauguration")]:
    s = d.loc[a:b]
    p(f"  {lab:24s} {(100*(s.S_HUCZ.iloc[-1]-s.S_HUCZ.iloc[0]))/(s.P.iloc[-1]-s.P.iloc[0]):+7.0f} bp/100pp")

# ------------------------------------------------------------------ regressions
def ols(y, X, hac=5):
    return sm.OLS(y, sm.add_constant(X), missing="drop").fit(
        cov_type="HAC", cov_kwds={"maxlags": hac})


def show(m, title):
    p(f"--- {title} ---")
    t = pd.DataFrame({"coef": m.params, "se": m.bse, "t": m.tvalues,
                      "p": m.pvalues}).round(4)
    p(t.to_string())
    p(f"N = {int(m.nobs)}, R2 = {m.rsquared:.3f}")


ch = pd.DataFrame({
    "dS": d.S_HUCZ.diff(), "dHU": d.HU10Y.diff(), "dP": d.P.diff(),
    "dDE": d.DE10Y.diff(), "dUS": d.US10Y.diff(), "dVIX": d.VIX.diff(),
    "dBrent": d.lnBrent.diff(),
}).dropna(subset=["dS", "dP"])
CTRL = ["dDE", "dUS", "dVIX", "dBrent"]

hdr("4. DAILY-CHANGE REGRESSIONS  (yield in pp; x100 = bp)")
p(f"N = {len(ch)}, sd(dP) = {ch.dP.std():.4f}, sd(dS) = {ch.dS.std():.4f}")
show(ols(ch.dS, ch[["dP"]]), "M1  d(HU-CZ) on dP")
show(ols(ch.dS, ch[["dP"] + CTRL]), "M2  + global controls")
show(ols(ch.dHU, ch[["dP"] + CTRL]), "M3  d(HU10Y) on dP + controls")
show(ols(ch.loc[:"2026-04-10"].dS,
         ch.loc[:"2026-04-10", ["dP"] + CTRL]), "M4  pre-election only")
show(ols(ch.loc["2026-04-13":].dS,
         ch.loc["2026-04-13":, ["dP"] + CTRL]), "M5  post-election only")
upd = ch[ch.dP != 0]
show(ols(upd.dS, upd[["dP"] + CTRL]), f"M6  update days only (N={len(upd)})")
p("")
p("VERDICT: beta on dP is never significantly negative. Daily dose-response is NOT")
p("identified. dP is zero on most days and the one large move (22 Apr, +31 pp) comes")
p("ten days AFTER the spread had already fallen.")

# ------------------------------------------------------------------ monthly
hdr("5. MONTHLY / WEEKLY CHANGES  (the only horizon with real variation in P)")
for freq, lab in [("W", "weekly"), ("ME", "monthly")]:
    g = d.resample(freq).agg({"S_HUCZ": "last", "P": "last"}).dropna()
    g["dS"] = g.S_HUCZ.diff(); g["dP"] = g.P.diff(); g = g.dropna()
    m = ols(g.dS, g[["dP"]], hac=2)
    p(f"{lab}: N = {len(g)}, beta = {m.params.dP:.3f} "
      f"(se {m.bse.dP:.3f}, t {m.tvalues.dP:.2f}), R2 = {m.rsquared:.3f}")
    if lab == "monthly":
        p("  leave-one-out:")
        for dt in g.index:
            mm = ols(g.drop(dt).dS, g.drop(dt)[["dP"]], hac=2)
            p(f"    drop {dt.date()}: beta = {mm.params.dP:+.3f}, t = {mm.tvalues.dP:+.2f}, "
              f"p = {mm.pvalues.dP:.3f}")
p("")
p("VERDICT: the monthly slope is large and significant ONLY because of April 2026.")
p("Drop that month and the relation vanishes (beta ~ -0.5, t ~ -1.0).")

# ------------------------------------------------------------------ placebo
hdr("6. PLACEBO COUNTRIES  (spread vs Germany on dP, same controls)")
rows = []
for c, lab in [("HU10Y", "HU"), ("CZ10Y", "CZ"), ("PL10Y", "PL"), ("RO10Y", "RO"),
               ("SI10Y", "SI"), ("HR10Y", "HR"), ("AT10Y", "AT")]:
    sp = d[c] - d.DE10Y
    dd = pd.DataFrame({"dS": sp.diff(), "dP": d.P.diff(), "dDE": d.DE10Y.diff(),
                       "dUS": d.US10Y.diff(), "dVIX": d.VIX.diff(),
                       "dBrent": d.lnBrent.diff()}).dropna()
    mm = ols(dd.dS, dd[["dP"] + CTRL])
    rows.append({"country": lab, "beta_dP": mm.params.dP, "se": mm.bse.dP,
                 "t": mm.tvalues.dP, "N": int(mm.nobs)})
p(pd.DataFrame(rows).set_index("country").round(4).to_string())

# ------------------------------------------------------------------ continuous DiD
hdr("7. CONTINUOUS DiD PANEL  (country + date fixed effects)")
panel_c = [("HU10Y", "HU"), ("CZ10Y", "CZ"), ("PL10Y", "PL"), ("RO10Y", "RO"),
           ("SI10Y", "SI"), ("HR10Y", "HR"), ("AT10Y", "AT")]
longp = pd.concat([
    pd.DataFrame({"date": d.index, "country": lab, "y": d[c].values, "P": d.P.values})
    for c, lab in panel_c
]).dropna()
longp["HU"] = (longp.country == "HU").astype(float)
longp["PxHU"] = longp.P * longp.HU
longp["date_id"] = longp.date.factorize()[0]
longp["ctry_id"] = longp.country.factorize()[0]


def did(dfp, treated="HU"):
    x = dfp.copy()
    x["tr"] = (x.country == treated).astype(float)
    x["PxT"] = x.P * x.tr
    X = pd.get_dummies(x[["date_id", "ctry_id"]].astype("category"), drop_first=True)
    X = X.astype(float)
    X["PxT"] = x.PxT.values
    m = sm.OLS(x.y.values, sm.add_constant(X)).fit()
    return m.params["PxT"], m.bse["PxT"]


b, se = did(longp)
p(f"beta(P x HU) = {b:.4f} pp per unit P  = {100*b:.0f} bp per 100pp "
  f"(conventional se {se:.4f})")
p(f"N = {len(longp)}, countries = {longp.country.nunique()}")
p("Randomisation inference: re-label each country as 'treated' in turn")
stats = {}
for c in longp.country.unique():
    bb, _ = did(longp, c)
    stats[c] = bb
    p(f"  treated = {c}: beta = {bb:+.4f}")
rank = sum(v <= b for v in stats.values())
p(f"  HU is rank {rank} of {len(stats)} (most negative = strongest); "
  f"RI p-value = {rank/len(stats):.2f}")

# ------------------------------------------------------------------ market model
hdr("8. MARKET MODEL  (estimate on 2023-2025, forecast the event window)")
lm = long.dropna(subset=["HU10Y", "DE10Y", "US10Y", "VIX", "BRENT"]).copy()
lm["dHU"] = lm.HU10Y.diff(); lm["dDE"] = lm.DE10Y.diff(); lm["dUS"] = lm.US10Y.diff()
lm["dVIX"] = lm.VIX.diff(); lm["dBrent"] = np.log(lm.BRENT).diff()
lm = lm.dropna(subset=["dHU", "dDE", "dUS", "dVIX", "dBrent"])
train = lm.loc[:"2025-06-30"]
mm = sm.OLS(train.dHU, sm.add_constant(train[["dDE", "dUS", "dVIX", "dBrent"]])).fit()
p(f"Training window: {train.index.min().date()} to {train.index.max().date()} "
  f"(N = {len(train)})")
p(pd.DataFrame({"coef": mm.params, "se": mm.bse, "t": mm.tvalues}).round(4).to_string())
p(f"R2 = {mm.rsquared:.3f}")
test = lm.loc["2025-07-01":"2026-05-08"].copy()
X = sm.add_constant(test[["dDE", "dUS", "dVIX", "dBrent"]])
test["resid"] = test.dHU - mm.predict(X)
test["cum_resid"] = test.resid.cumsum()
p("")
p("Cumulative Hungary-specific residual (bp):")
for dt in ["2025-07-25", "2026-02-27", "2026-04-09", "2026-04-30", "2026-05-08"]:
    try:
        p(f"  {dt}: {100*test.loc[:dt,'cum_resid'].iloc[-1]:+.0f} bp")
    except IndexError:
        pass
p(f"Total residual over the window: {100*test.cum_resid.iloc[-1]:+.0f} bp")
p(f"Actual HU10Y change over the window: "
  f"{100*(test.HU10Y.iloc[-1]-test.HU10Y.iloc[0]):+.0f} bp")

# ------------------------------------------------------------------ figures
fig, ax = plt.subplots(figsize=(9.2, 4.8))
ax.plot(d.index, d.S_HUCZ, color="#1f4e79", lw=1.7, label="HU-CZ 10Y spread (pp)")
ax.set_ylabel("HU-CZ 10Y spread, pp", color="#1f4e79")
ax.tick_params(axis="y", labelcolor="#1f4e79")
ax2 = ax.twinx()
ax2.plot(d.index, d.P, color="#c00000", lw=1.5, ls="--",
         label="P(Orbán does not remain PM)")
ax2.set_ylabel("Polymarket probability", color="#c00000")
ax2.tick_params(axis="y", labelcolor="#c00000")
ax2.set_ylim(0, 1.05)
for x, lab in [("2026-02-22", "poll shift"), ("2026-04-12", "election"),
               ("2026-05-09", "inauguration")]:
    ax.axvline(pd.Timestamp(x), color="grey", lw=0.8, ls=":")
    ax.annotate(lab, (pd.Timestamp(x), ax.get_ylim()[1]), fontsize=8, rotation=90,
                va="top", ha="right", color="grey")
ax.set_title("Hungarian sovereign spread and market-implied regime change")
fig.tight_layout()
fig.savefig(OUT / "fig1_prob_vs_spread.png", dpi=160)
plt.close(fig)

g = d.resample("ME").agg({"S_HUCZ": "last", "P": "last"}).dropna()
g["dS"] = 100 * g.S_HUCZ.diff(); g["dP"] = 100 * g.P.diff(); g = g.dropna()
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.axhline(0, color="black", lw=0.7); ax.axvline(0, color="black", lw=0.7)
ax.scatter(g.dP, g.dS, s=45, color="#1f4e79", zorder=3)
for dt, r in g.iterrows():
    ax.annotate(dt.strftime("%b-%y"), (r.dP, r.dS), fontsize=7,
                xytext=(4, 3), textcoords="offset points", color="grey")
b_, a_ = np.polyfit(g.dP, g.dS, 1)
xs = np.linspace(g.dP.min(), g.dP.max(), 10)
ax.plot(xs, a_ + b_ * xs, color="#c00000", lw=1.4)
ax.set_xlabel("change in P(Orbán loses), pp")
ax.set_ylabel("change in HU-CZ spread, bp")
ax.set_title("Monthly changes: probability vs spread")
fig.tight_layout()
fig.savefig(OUT / "fig2_monthly_scatter.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9.2, 4.4))
ax.axhline(0, color="black", lw=0.7)
ax.plot(test.index, 100 * test.cum_resid, color="#1f4e79", lw=1.6)
ax.set_ylabel("cumulative Hungary-specific residual, bp")
ax.set_title("Market model: Hungary-specific yield component, Jul 2025 - May 2026")
for x, lab in [("2026-02-22", "poll shift"), ("2026-04-12", "election")]:
    ax.axvline(pd.Timestamp(x), color="grey", lw=0.8, ls=":")
fig.tight_layout()
fig.savefig(OUT / "fig3_market_model.png", dpi=160)
plt.close(fig)

p("")
p(f"Figures written to {OUT}")
(OUT / "results.txt").write_text("\n".join(L))
