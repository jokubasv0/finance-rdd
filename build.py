"""Build merged daily panel: Polymarket regime-change probability + sovereign yields."""
import json
import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent / "raw"
OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)


def load_polymarket(name: str) -> pd.Series:
    d = json.loads((RAW / f"pm_{name}.json").read_text())
    s = pd.Series(
        {pd.to_datetime(p["t"], unit="s").normalize(): p["p"] for p in d["history"]}
    )
    return s.sort_index().rename(name)


def load_investing(name: str) -> pd.Series:
    d = json.loads((RAW / f"inv_{name}.json").read_text())
    rows = {
        pd.to_datetime(r["rowDateTimestamp"]).tz_localize(None).normalize(): r[
            "last_closeRaw"
        ]
        for r in d["data"]
    }
    return pd.Series(rows).sort_index().rename(name)


def load_yahoo(name: str) -> pd.Series:
    d = json.loads((RAW / f"yh_{name}.json").read_text())["chart"]["result"][0]
    ts = pd.to_datetime(d["timestamp"], unit="s").normalize()
    vals = d["indicators"]["quote"][0]["close"]
    return pd.Series(vals, index=ts).dropna().rename(name)


pm = pd.concat(
    [load_polymarket(n) for n in ["orban", "magyar", "tisza"]], axis=1
)
# P(Orban does NOT remain PM)
pm["p_notorban"] = 1 - pm["orban"]

yld = pd.concat(
    [
        load_investing(n)
        for n in [
            "HU10Y", "HU5Y", "CZ10Y", "DE10Y", "PL10Y", "RO10Y",
            "CZ2Y", "DE2Y", "SI10Y", "BG10Y", "HR10Y", "AT10Y",
        ]
    ],
    axis=1,
)

yho = pd.concat(
    [load_yahoo(n) for n in ["US10Y", "VIX", "BRENT", "EURUSD", "USDHUF"]], axis=1
)

df = pm.join(yld, how="outer").join(yho, how="outer").sort_index()

# Restrict to the Polymarket market life
df = df.loc["2025-07-24":"2026-11-14"]

print("rows", len(df))
print("\ncoverage (non-null):")
print(df.notna().sum().to_string())
print("\nfirst non-null date per series:")
print(df.apply(lambda s: s.first_valid_index()).to_string())
print("\nlast non-null date per series:")
print(df.apply(lambda s: s.last_valid_index()).to_string())

df.to_csv(OUT / "panel_daily.csv")
print("\nsaved", OUT / "panel_daily.csv")
print(df.tail(8).round(3).to_string())
