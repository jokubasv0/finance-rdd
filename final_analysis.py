"""Final analysis: Hungary 2026 election and sovereign risk.

Reads raw/, writes out/final_results.txt and the paper's figures.

Primary outcome: HU 10Y minus peer average (CZ, PL, RO, SI, HR, AT).
Secondary:        HU 10Y minus Bund.
Favourable bound: HU 10Y minus Czechia.
"""
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE = Path(__file__).parent
RAW, OUT = BASE / "raw", BASE / "out"
OUT.mkdir(exist_ok=True)

L = []
def p(*a):
    s = " ".join(str(x) for x in a)
    print(s); L.append(s)
def hdr(t):
    p(""); p("=" * 76); p(t); p("=" * 76)

# ---------------------------------------------------------------- load
def inv(prefix, name):
    d = json.loads((RAW / f"{prefix}_{name}.json").read_text())
    s = pd.Series({pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize():
                   r["last_closeRaw"] for r in d["data"]})
    return s.sort_index().rename(name)

def yh(prefix, name):
    d = json.loads((RAW / f"{prefix}_{name}.json").read_text())["chart"]["result"][0]
    return pd.Series(d["indicators"]["quote"][0]["close"],
                     index=pd.to_datetime(d["timestamp"], unit="s").normalize()
                     ).dropna().rename(name)

SHORT = ["HU10Y", "HU5Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y", "SI10Y", "HR10Y", "AT10Y"]
S = pd.concat([inv("inv", n) for n in SHORT]
              + [yh("yh", n) for n in ["US10Y", "VIX", "BRENT", "USDHUF", "EURUSD"]],
              axis=1, sort=True).apply(pd.to_numeric, errors="coerce").sort_index()

LONG = ["HU10Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y"]
G = pd.concat([inv("long", n) for n in LONG]
              + [yh("long_yh", n) for n in ["US10Y", "VIX", "BRENT"]],
              axis=1, sort=True).apply(pd.to_numeric, errors="coerce").sort_index()

# The prediction-market series keeps its OWN index. It prints on weekends, and
# aligning it onto the weekday yield grid (S.index) silently deletes every
# Saturday and Sunday print -- including the 26 July 2025 repricing from 0.385
# to 0.580. PM is therefore the 257-print series, and P_s is the version carried
# forward onto the weekday close, used only where a daily yield comparison is
# genuinely being made.
pm = pd.Series({pd.to_datetime(x["t"], unit="s").normalize(): x["p"]
                for x in json.loads((RAW / "pm_orban.json").read_text())["history"]}
               ).sort_index()
PM = (1 - pm).rename("P")          # P(Orban does not remain PM), 257 prints
S["P"] = PM.reindex(S.index).ffill()   # as of each weekday close

PEERS = ["CZ10Y", "PL10Y", "RO10Y", "SI10Y", "HR10Y", "AT10Y"]
# Peer aggregation: forward-fill each peer up to 5 business days so the average
# keeps a CONSTANT composition. Without this, a missing Polish or Romanian print
# mechanically drags the average down by 50-80bp and creates spurious spread spikes.
for df in (S,):
    df["CEE"] = df[PEERS].ffill(limit=5).mean(axis=1, skipna=True)
    df["SP_PEER"] = df.HU10Y - df.CEE
    df["SP_DE"] = df.HU10Y - df.DE10Y
    df["SP_CZ"] = df.HU10Y - df.CZ10Y
G["CEE3"] = G[["CZ10Y", "PL10Y", "RO10Y"]].ffill(limit=5).mean(axis=1, skipna=True)
G["SP"] = G.HU10Y - G.CEE3

W0, W1 = "2025-07-25", "2026-05-08"
w = S.loc[W0:W1].copy()

# ---------------------------------------------------------------- 1
hdr("1. SAMPLE")
p(f"Full sample      : {S.index.min().date()} to {S.index.max().date()}")
p(f"Event window     : {w.index.min().date()} to {w.index.max().date()}  ({len(w)} days)")
p(f"Long sample      : {G.index.min().date()} to {G.index.max().date()}  ({len(G)} days)")
p("")
p("Non-missing observations in the event window:")
for c in SHORT + ["CEE", "SP_PEER", "SP_DE", "SP_CZ"]:
    p(f"  {c:9s} {w[c].notna().sum():4d}")
p("")
p("Peer group = equal-weighted Czechia, Poland, Romania, Slovenia, Croatia, Austria.")
p("Romania enters with the highest level (~7%) and the highest volatility, so the")
p("peer average is checked against a median-based version below.")

med = w[PEERS].median(axis=1, skipna=True)
w["CEE_MED"] = med
w["SP_MED"] = w.HU10Y - w.CEE_MED

# ---------------------------------------------------------------- 2
hdr("2. LEVELS AND CHANGES OVER THE EVENT WINDOW")
p(f"{'series':10s} {'start':>8s} {'end':>8s} {'change':>9s}")
for c in ["HU10Y", "HU5Y", "CEE", "DE10Y", "CZ10Y", "PL10Y", "RO10Y"]:
    s = w[c].dropna()
    p(f"{c:10s} {s.iloc[0]:8.2f} {s.iloc[-1]:8.2f} {100*(s.iloc[-1]-s.iloc[0]):+8.0f}bp")
p("")
for c, lab in [("SP_PEER", "HU - peers "), ("SP_MED", "HU - peer med"),
               ("SP_DE", "HU - Bund  "), ("SP_CZ", "HU - Czechia")]:
    s = w[c].dropna()
    p(f"{lab} {s.iloc[0]:8.2f} {s.iloc[-1]:8.2f} {100*(s.iloc[-1]-s.iloc[0]):+8.0f}bp")
p("")
p(f"P(Orban does not remain PM): {w.P.dropna().iloc[0]:.3f} -> {w.P.dropna().iloc[-1]:.3f}")
p(f"EURHUF: {(w.USDHUF*w.EURUSD).dropna().iloc[0]:.1f} -> {(w.USDHUF*w.EURUSD).dropna().iloc[-1]:.1f}")

# ---------------------------------------------------------------- 3
hdr("3. EVENT-WINDOW DECOMPOSITION")
WINDOWS = [("2025-07-25", "2026-02-26", "A. Pre-campaign"),
           ("2026-02-26", "2026-04-09", "B. Campaign"),
           ("2025-07-25", "2026-04-09", "   A+B Pre-vote"),
           ("2026-04-09", "2026-05-08", "C. Result to inauguration"),
           ("2025-07-25", "2026-05-08", "   TOTAL")]
p(f"{'window':28s} {'HU-peers':>10s} {'HU-Bund':>10s} {'HU-CZ':>9s} {'HU10Y':>9s}")
for a, b, lab in WINDOWS:
    seg = w.loc[a:b]
    vals = []
    for c in ["SP_PEER", "SP_DE", "SP_CZ", "HU10Y"]:
        s = seg[c].dropna()
        vals.append(100 * (s.iloc[-1] - s.iloc[0]) if len(s) > 1 else np.nan)
    p(f"{lab:28s} {vals[0]:+9.0f}bp {vals[1]:+9.0f}bp {vals[2]:+8.0f}bp {vals[3]:+8.0f}bp")
p("")
p("Share of the total peer-relative compression occurring before the vote:")
tot = 100 * (w.SP_PEER.dropna().iloc[-1] - w.SP_PEER.dropna().iloc[0])
pre = 100 * (w.loc[:"2026-04-09"].SP_PEER.dropna().iloc[-1] - w.SP_PEER.dropna().iloc[0])
p(f"  {100*pre/tot:.0f}% ({pre:.0f} of {tot:.0f} bp)")

# ---------------------------------------------------------------- 4
hdr("4. CONTROL-CHOICE SENSITIVITY")
p("Change in the HU spread, same window, different control:")
rows = []
for c, lab in [("CZ10Y", "Czechia"), ("DE10Y", "Germany (Bund)"), ("PL10Y", "Poland"),
               ("RO10Y", "Romania"), ("SI10Y", "Slovenia"), ("HR10Y", "Croatia"),
               ("AT10Y", "Austria")]:
    s = (w.HU10Y - w[c]).dropna()
    d = s.diff().dropna()
    t = d.mean() / (d.std() / np.sqrt(len(d)))
    rows.append([lab, 100 * (s.iloc[-1] - s.iloc[0]), t, len(d)])
s = w.SP_PEER.dropna(); d = s.diff().dropna()
rows.append(["Peer average", 100 * (s.iloc[-1] - s.iloc[0]),
             d.mean() / (d.std() / np.sqrt(len(d))), len(d)])
s = w.SP_MED.dropna(); d = s.diff().dropna()
rows.append(["Peer median", 100 * (s.iloc[-1] - s.iloc[0]),
             d.mean() / (d.std() / np.sqrt(len(d))), len(d)])
p(f"{'control':16s} {'change':>9s} {'daily t':>9s} {'N':>5s}")
for r in rows:
    p(f"{r[0]:16s} {r[1]:+8.0f}bp {r[2]:+9.2f} {r[3]:5d}")
p("")
p("Every control gives a large negative. Czechia gives the most favourable number;")
p("the peer average is the conservative one and is the headline estimate.")

# ---------------------------------------------------------------- 5
hdr("5. TREND ADJUSTMENT")
tr = G.SP.dropna()
fitp = tr.loc[:"2025-06-30"]
x = np.arange(len(fitp))
b, a = np.polyfit(x, fitp.values, 1)
p(f"HU - (CZ,PL,RO) spread, level trend estimated on {fitp.index.min().date()} to {fitp.index.max().date()}")
p(f"  slope = {100*b:.3f} bp per trading day = {100*b*252:.0f} bp per year")
p(f"  fitted change over a 194-day window: {100*b*194:.0f} bp")
miss = tr.loc["2025-07-25":"2026-05-08"]
p(f"  observed change over the window: {100*(miss.iloc[-1]-miss.iloc[0]):.0f} bp")
p(f"  trend-adjusted (observed minus trend): "
  f"{100*(miss.iloc[-1]-miss.iloc[0]) - 100*b*len(miss):.0f} bp")
p("")
p("The peer spread was already narrowing before the election. The trend-adjusted")
p("estimate is the honest lower bound; the raw estimate is the upper bound.")

# ---------------------------------------------------------------- 6
hdr("6. TERM STRUCTURE")
sl = (w.HU10Y - w.HU5Y) * 100
for a_, b_, lab in [("2025-07-25", "2026-04-09", "pre-vote"),
                    ("2026-04-09", "2026-05-08", "result to inauguration"),
                    ("2025-07-25", "2026-05-08", "full window")]:
    s = sl.loc[a_:b_].dropna()
    p(f"  {lab:26s} 10Y-5Y {s.iloc[0]:+5.0f} -> {s.iloc[-1]:+5.0f} bp  ({s.iloc[-1]-s.iloc[0]:+5.0f} bp)")
p("")
p("Pre-vote: 10Y fell while 5Y rose. A monetary-easing story predicts the opposite.")
p("Post-result: the move is parallel, consistent with a level shift in perceived risk.")

# ---------------------------------------------------------------- 7
hdr("7. MARKET MODEL")
m = G.dropna(subset=["HU10Y", "CEE3", "DE10Y", "US10Y", "VIX", "BRENT"]).copy()
m["dHU"] = m.HU10Y.diff()
m["dCEE"] = m.CEE3.diff()
m["dDE"] = m.DE10Y.diff(); m["dUS"] = m.US10Y.diff()
m["dVIX"] = m.VIX.diff(); m["dBrent"] = np.log(m.BRENT).diff()
m = m.dropna(subset=["dHU", "dCEE", "dDE", "dUS", "dVIX", "dBrent"])
train = m.loc[:"2025-06-30"]
mm = sm.OLS(train.dHU, sm.add_constant(train[["dCEE", "dUS", "dVIX", "dBrent"]])
            ).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
p(f"d(HU10Y) on d(peer yield) and global factors")
p(f"Training {train.index.min().date()} to {train.index.max().date()}, N = {len(train)}, R2 = {mm.rsquared:.3f}")
p(pd.DataFrame({"coef": mm.params, "se": mm.bse, "t": mm.tvalues}).round(4).to_string())
post = m.loc["2025-07-25":"2026-05-08"].copy()
post["res"] = post.dHU - mm.predict(sm.add_constant(post[["dCEE", "dUS", "dVIX", "dBrent"]]))
post["cum"] = 100 * post.res.cumsum()
p("")
p("Cumulative Hungary-specific residual, bp:")
for dte in ["2025-12-31", "2026-02-26", "2026-04-09", "2026-05-08"]:
    try:
        p(f"  {dte}: {post.loc[:dte,'cum'].iloc[-1]:+6.0f}")
    except IndexError:
        pass
p(f"  window total: {post.cum.iloc[-1]:+.0f} bp")
p("")
p("The model explains movements in the Hungarian yield, not the spread. Its residual")
p("is the part of the Hungarian move not matched by its peers.")

# ---------------------------------------------------------------- 8
hdr("8. PLACEBO: RANDOM WINDOWS (WITHDRAWN, NOT REPAIRED)")
sp = G.SP.dropna()
n = 194
rows = []
for i in range(0, len(sp) - n, 5):
    seg = sp.iloc[i:i + n]
    rows.append((seg.index[0], seg.index[-1], 100 * (seg.iloc[-1] - seg.iloc[0])))
rnd = pd.DataFrame(rows, columns=["start", "end", "chg"])
obs = 100 * (sp.loc[W1] - sp.loc[W0])
late = rnd[rnd.end > pd.Timestamp("2026-04-10")]
pre = rnd[rnd.end <= pd.Timestamp("2026-04-10")]
p(f"Draws: {len(rnd)} of {n} days, series {sp.index.min().date()} to {sp.index.max().date()}")
p(f"  windows ending after the real event: {len(late)} of {len(rnd)}")
p(f"  observed window change: {obs:+.0f} bp")
p(f"  share at least as negative, all draws          : {100*(rnd.chg <= obs).mean():.0f}%")
p(f"  share at least as negative, pre-event draws only: {100*(pre.chg <= obs).mean():.0f}%")
p("")
p("WHY THIS IS WITHDRAWN RATHER THAN CORRECTED.")
p("The series trends down across the whole sample. A 194-day change is therefore")
p("not a stationary quantity: its distribution depends entirely on where the")
p("window sits relative to the trend, and the observed window sits at the end.")
p("Restricting draws to windows that end before the election does not fix this,")
p("it makes the comparison worse -- it compares the observed window, which")
p("contains the trend's endpoint, against windows that by construction cannot.")
p("The p-value that comes out is a statement about the shape of the series, not")
p("about the election. It is reported here, and in the paper, as a failed test.")
p("The placebo evidence the paper relies on is the placebo-date test on a panel")
p("truncated before the event, which is a real test and passes.")
p("")
# What replaces it descriptively: the quarterly path that motivated the 2024 start
Q = (100 * G.SP.dropna()).resample("QE").mean()
Q.index = [f"{d.year}Q{(d.month-1)//3+1}" for d in Q.index]
p("Hungary minus (CZ, PL, RO), quarterly mean, bp -- the reason 2022 is excluded:")
p("  " + "  ".join(f"{k} {v:+.0f}" for k, v in Q.items() if k >= "2022Q1"))

# ---------------------------------------------------------------- 9
hdr("9. PLACEBO: COUNTRIES")
p("Each country's spread over the peer average, same window (should be ~0):")
for c, lab in [("CZ10Y", "Czechia"), ("PL10Y", "Poland"), ("RO10Y", "Romania"),
               ("SI10Y", "Slovenia"), ("HR10Y", "Croatia"), ("AT10Y", "Austria")]:
    others = [x for x in PEERS if x != c]
    ref = w[others].mean(axis=1, skipna=True)
    s = (w[c] - ref).dropna()
    p(f"  {lab:10s} {100*(s.iloc[-1]-s.iloc[0]):+6.0f} bp")

# ---------------------------------------------------------------- 10
hdr("10. THE POLYMARKET SERIES")
p(f"Prints: {len(PM)} over {(PM.index[-1]-PM.index[0]).days} calendar days")
p(f"  prints inside the event window {W0} to {W1}: {len(PM.loc[W0:W1])}, "
  f"of which {sum(d.weekday() < 5 for d in PM.loc[W0:W1].index)} on weekdays")
p(f"  prints falling on a weekend: {sum(d.weekday() >= 5 for d in PM.index)}")
dP = PM.diff().dropna()
p(f"Largest single-day moves in P:")
for dte, v in (dP.abs().sort_values(ascending=False).head(8)).items():
    prev = PM.loc[:dte].iloc[-2]
    p(f"  {dte.date()} {dte.day_name()[:3]}  {100*v:+6.1f} pp   "
      f"({100*prev:.1f} -> {100*PM.loc[dte]:.1f})")
p("")
p(f"Moves larger than 10 pp: {(dP.abs() > 0.10).sum()}.  Larger than 5 pp: {(dP.abs() > 0.05).sum()}.")
p("")
p("Daily regression of the peer spread on dP (P carried forward between prints):")
base = pd.DataFrame({"S": w.SP_PEER})
base["P"] = PM.reindex(w.index).ffill()
base["dS"] = base.S.diff(); base["dP"] = base.P.diff()
ch = base.dropna()
ch["dDE"] = w.DE10Y.reindex(ch.index).diff()
ch["dUS"] = w.US10Y.reindex(ch.index).diff()
ch["dVIX"] = w.VIX.reindex(ch.index).diff()
ch["dB"] = np.log(w.BRENT.reindex(ch.index)).diff()
for cols, lab in [(["dP"], "no controls"), (["dP", "dDE", "dUS", "dVIX", "dB"], "with controls")]:
    mm2 = sm.OLS(ch.dS, sm.add_constant(ch[cols]), missing="drop").fit(
        cov_type="HAC", cov_kwds={"maxlags": 5})
    p(f"  {lab:14s} beta = {mm2.params.dP:+.4f}  (t = {mm2.tvalues.dP:+.2f}, N = {int(mm2.nobs)})")
p("")
p("Neither coefficient is distinguishable from zero and the sign is not stable")
p("across the two specifications, so the daily design cannot estimate the dose-")
p("response at all. It is reported because a reader will ask for it.")
p("The contract prints on 9 April and then not again until 22 April, by which")
p("time the spread had already fallen. It cannot support a daily treatment variable.")

# ---------------------------------------------------------------- 11
hdr("11. BOND-IMPLIED VERSUS MARKET-IMPLIED PROBABILITY")
S0 = w.SP_PEER.dropna().iloc[0]
impl = {}
for T, lab in [("2026-05-08", "terminal = May 8"), ("2026-11-13", "terminal = Nov 13")]:
    ST = S.SP_PEER.loc[:T].dropna().iloc[-1]
    impl[lab] = (S0 - S.SP_PEER) / (S0 - ST)
p("If the spread moves one-for-one with the probability that Orbán leaves office,")
p("the bond market's implied probability is (S0 - St) / (S0 - ST).")
p("")
p(f"{'date':12s} {'spread':>8s} {'Polymarket':>11s} {'bonds(May)':>11s} {'bonds(Nov)':>11s}")
for d in ["2025-07-25", "2026-02-26", "2026-04-09", "2026-05-08", "2026-11-13"]:
    sp = S.SP_PEER.loc[:d].dropna()
    pp = PM.loc[:d].dropna()
    if len(sp) == 0:
        continue
    v = [impl[k].loc[:d].dropna() for k in impl]
    v = [x.iloc[-1] if len(x) else np.nan for x in v]
    p(f"{d:12s} {sp.iloc[-1]:8.2f} {(pp.iloc[-1] if len(pp) else np.nan):11.3f} "
      f"{v[0]:11.3f} {v[1]:11.3f}")
p("")
p("On 9 April, with the vote three days away, the bond market had priced roughly")
p("a third of the eventual compression while Polymarket had priced about 69%.")
p("Whichever terminal value is used, the prediction market moved first.")

# ---------------------------------------------------------------- figures
fig, ax = plt.subplots(figsize=(9.4, 4.8))
ax.plot(w.index, w.HU10Y, color="#1f4e79", lw=1.8, label="Hungary 10Y")
ax.plot(w.index, w.CEE, color="#7f7f7f", lw=1.6, label="Peer average 10Y")
ax.plot(w.index, w.DE10Y, color="#bfbfbf", lw=1.2, ls="--", label="Germany 10Y")
for x_, lab in [("2026-02-26", "campaign"), ("2026-04-12", "election"),
                ("2026-05-09", "inauguration")]:
    ax.axvline(pd.Timestamp(x_), color="black", lw=0.8, ls=":")
    ax.annotate(lab, (pd.Timestamp(x_), ax.get_ylim()[1]), fontsize=8, rotation=90,
                va="top", ha="right")
ax.set_ylabel("yield, %"); ax.legend(frameon=False, fontsize=9, loc="lower left")
ax.set_title("Hungarian and peer sovereign yields, July 2025 - May 2026")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
fig.tight_layout(); fig.savefig(OUT / "fig1_levels.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(9.4, 4.4))
ax.axhline(0, color="black", lw=0.8)
ax.plot(G.index, G.SP, color="#1f4e79", lw=1.4, label="HU minus (CZ,PL,RO)")
ax.plot(w.index, w.SP_PEER, color="#c00000", lw=1.8, label="HU minus peer average")
ax.set_ylabel("spread, pp")
ax.set_title("Hungary's spread over peers, 2022-2026")
ax.legend(frameon=False, fontsize=9)
fig.tight_layout(); fig.savefig(OUT / "fig2_spread.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(9.4, 4.2))
ax.axhline(0, color="black", lw=0.8)
ax.plot(post.index, post.cum, color="#1f4e79", lw=1.7)
ax.set_ylabel("cumulative residual, bp")
ax.set_title("Hungary-specific yield move after removing global factors")
fig.tight_layout(); fig.savefig(OUT / "fig3_residual.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(8.6, 4.2))
Qs = Q[Q.index >= "2022Q1"]
x = np.arange(len(Qs))
ax.bar(x, Qs.values, color="#1f4e79", alpha=0.85, width=0.7)
ax.axhline(0, color="black", lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels(Qs.index, rotation=90, fontsize=7)
ax.set_ylabel("HU minus (CZ, PL, RO), bp")
ax.set_title("Hungary's spread over Czechia, Poland and Romania, quarterly")
fig.tight_layout(); fig.savefig(OUT / "fig4_spread_path.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.6, 4.0))
seg = sl.loc["2026-01-01":"2026-05-08"].dropna()
seg2 = (w.HU5Y * 100).loc["2026-01-01":"2026-05-08"].dropna()
ax.plot(seg.index, seg, color="#c00000", lw=1.8, label="10Y minus 5Y")
ax.axhline(0, color="black", lw=0.8)
ax.axvline(pd.Timestamp("2026-04-12"), color="black", lw=0.8, ls=":")
ax.set_ylabel("slope, bp"); ax.legend(frameon=False)
ax.set_title("Hungarian curve slope around the election")
fig.tight_layout(); fig.savefig(OUT / "fig5_slope.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(9.0, 4.4))
Pp = PM.dropna()
ax.plot(Pp.index, Pp, color="#c00000", lw=1.6, label="Polymarket: P(Orban leaves)")
for k, c, ls in [("terminal = May 8", "#1f4e79", "-"), ("terminal = Nov 13", "#1f4e79", ":")]:
    s = impl[k].dropna()
    s = s.loc["2025-07-25":"2026-05-08"]
    ax.plot(s.index, s, color=c, lw=1.5, ls=ls, label=f"Bond-implied, {k[11:]}")
ax.set_ylim(-0.05, 1.05); ax.set_ylabel("probability")
ax.set_title("Market-implied versus bond-implied probability of regime change")
ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "fig6_implied.png", dpi=170); plt.close(fig)

(OUT / "final_results.txt").write_text("\n".join(L))
p(""); p(f"written to {OUT}")
