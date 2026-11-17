"""One deck-only figure: where the 160 basis points were given up.

The paper reports this as Table 3. As a slide it needs a shape, not a table:
three segments and a total, with the pre-vote share called out.

Reads raw/, so it cannot drift from final_results.txt.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAW = Path(__file__).parent / "raw"
OUT = Path(__file__).parent / "out"

NAMES = ["HU10Y", "CZ10Y", "PL10Y", "RO10Y", "SI10Y", "HR10Y", "AT10Y"]
PEERS = ["CZ10Y", "PL10Y", "RO10Y", "SI10Y", "HR10Y", "AT10Y"]


def series(name):
    d = json.loads((RAW / f"inv_{name}.json").read_text())
    return pd.Series(
        {
            pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize():
                r["last_closeRaw"]
            for r in d["data"]
        }
    ).sort_index().rename(name)


px = pd.concat([series(n) for n in NAMES], axis=1, sort=True)
px = px.apply(pd.to_numeric, errors="coerce")
spread = px.HU10Y - px[PEERS].ffill(limit=5).mean(axis=1, skipna=True)

W0, W1 = pd.Timestamp("2025-08-04"), pd.Timestamp("2026-05-08")
CUT, VOTE = pd.Timestamp("2026-02-26"), pd.Timestamp("2026-04-09")


def at(d):
    return float(spread.loc[:d].dropna().iloc[-1])


s0, s1, s2, s3 = at(W0), at(CUT), at(VOTE), at(W1)
segs = [
    ("Pre-campaign\n4 Aug → 26 Feb", s1 - s0, "#7d97b3"),
    ("Campaign\n26 Feb → 9 Apr", s2 - s1, "#14385c"),
    ("Result → inauguration\n9 Apr → 8 May", s3 - s2, "#a5142e"),
]
total = s3 - s0

fig, ax = plt.subplots(figsize=(7.4, 3.4))
fig.subplots_adjust(left=0.245, right=0.985, top=0.79, bottom=0.235)

labels = ["Pre-campaign", "Campaign", "Result → inauguration", "Total"]
cum = 0.0
for i, (lab, d, col) in enumerate(segs):
    bp = d * 100
    y = 3 - i
    ax.barh(y, bp, left=cum, height=0.5, color=col)
    txt = f"{bp:+.0f} bp".replace("-", "\u2212")
    if abs(bp) >= 30:                       # label inside the bar, white
        ax.text(cum + bp / 2, y, txt, ha="center", va="center",
                color="white", fontsize=11.5, fontweight="bold", zorder=6)
    else:                                   # too narrow: label above it
        ax.text(cum + bp / 2, y + 0.30, txt, ha="center", va="bottom",
                color="#0e243b", fontsize=11, fontweight="bold", zorder=6)
    ax.plot([cum + bp, cum + bp], [y - 0.25, y - 0.75], color="#aab3c0",
            lw=0.8, ls=":")
    cum += bp

ax.barh(0, cum, left=0, height=0.5, color="#0e243b")
ax.text(cum / 2, 0, f"{cum:+.0f} bp".replace("-", "\u2212"), ha="center", va="center", color="white",
        fontsize=12.5, fontweight="bold")

ax.set_yticks([3, 2, 1, 0])
ax.set_yticklabels(labels, fontsize=10)
ax.set_ylim(-0.55, 3.55)
ax.set_xlim(-178, 12)
ax.set_xlabel("change in the ten-year spread, basis points", fontsize=9.5,
              labelpad=3)
ax.axvline(0, color="#141b26", lw=0.9)
ax.grid(axis="x", color="#e8ecf1", lw=0.7)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)

pre = (s2 - s0) * 100
post = (s3 - s2) * 100
fig.text(0.245, 0.925, "Where the 160 basis points went", fontsize=12.5,
         color="#14385c", fontweight="bold")
fig.text(0.245, 0.858,
         f"{abs(pre):.0f} bp before the vote ({abs(pre) / abs(cum) * 100:.0f}%), "
         f"{abs(post):.0f} after it ({abs(post) / abs(cum) * 100:.0f}%)",
         fontsize=10, color="#576170")
fig.text(0.245, 0.018, "Hungary minus the six-peer average; 4 August 2025 to 8 May 2026",
         fontsize=8.5, color="#939caa")
fig.savefig(OUT / "deck_timing.png", dpi=170)
print(f"wrote deck_timing.png   segments {[round(s[1] * 100, 1) for s in segs]}  "
      f"total {cum:.1f} bp")
