"""Re-derive REPORT.md 3.4 - where one stock ranks under each set of weights.

    python rederive_section34.py [YYYY-MM-DD] [TICKER ...]

REPORT.md 3.4 makes a claim that cannot be checked from the page alone: that the
same stock on the same day ranks near the top for one profile and near the bottom
for another. The weighted totals follow from the z-scores printed there, but the
RANKS depend on all 95 stocks, so they need a run.

This reproduces run_today.py's pipeline exactly - same windows, same >=130-day
minimum, same winsorised z-scores, same sector neutralisation - but truncates
prices at a chosen date so a dated claim in the report stays reproducible.

It reads its weights from factors.py like everything else. Do not copy them here;
that is the failure mode this repo keeps logging.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import yfinance as yf

from factors import FACTORS, PROFILES
from roe_data import roe_asof, neutral_fill              # point-in-time ROE, see roe_data.py

HERE = os.path.dirname(os.path.abspath(__file__))
ASOF = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2026-09-01")
TARGETS = sys.argv[2:] or ["PTT.BK", "GUNKUL.BK"]


def main():
    uni = json.load(open(os.path.join(HERE, "universe.json"), encoding="utf-8"))
    meta = {s["ticker"]: s["sector"] for s in uni["stocks"]}
    tickers = list(meta)
    print(f"{len(tickers)} tickers, prices truncated at {ASOF.date()}")

    px = yf.download(tickers,
                     start=(ASOF - pd.DateOffset(years=2, days=10)).date(),
                     end=(ASOF + pd.Timedelta(days=1)).date(),
                     auto_adjust=True, progress=False)["Close"]
    px = px.loc[px.index <= ASOF].dropna(how="all")
    print(f"history: {px.index.min().date()} -> {px.index.max().date()} ({len(px)} days)")

    rows = {}
    for t in tickers:
        s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
        if len(s) < 130:
            continue
        rows[t] = dict(momentum=s.iloc[-1] / s.iloc[-126] - 1,
                       roe=roe_asof(t, s.index[-1]),
                       quality=-s.pct_change().tail(252).std() * np.sqrt(252),
                       health=(s.tail(252) / s.tail(252).cummax() - 1).min())
    df = pd.DataFrame(rows).T
    df["roe"] = neutral_fill(list(df["roe"]))   # see roe_data.py
    df["sector"] = [meta[t] for t in df.index]
    print(f"scored: {len(df)} of {len(tickers)} stocks\n")

    def z(c):
        c = c.astype(float)
        sd = c.std(ddof=0)
        return ((c - c.mean()) / (sd if sd > 0 else 1.0)).clip(-3, 3)

    for f in FACTORS:
        df[f + "_z"] = z(df[f])
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    in_big = df["sector"].isin(big)
    for f in FACTORS:
        smean = df.groupby("sector")[f + "_z"].transform("mean")
        df[f + "_adj"] = df[f + "_z"] - smean.where(in_big, 0.0)

    scored = {}
    for name, W in PROFILES.items():
        tot = sum(W[f] * df[f + "_adj"] for f in FACTORS)
        scored[name] = (tot, tot.rank(ascending=False, method="min").astype(int))

    for tk in TARGETS:
        if tk not in df.index:
            print(f"{tk}: NOT SCORED (too little history, or not in universe.json)\n")
            continue
        r = df.loc[tk]
        print(f"=== {tk}  ({r['sector']}) ===")
        print("  sector-adjusted z: " +
              "   ".join(f"{f} {r[f + '_adj']:+.2f}" for f in FACTORS))
        for name in PROFILES:
            tot, rank = scored[name]
            print(f"  {name:<13} weighted total {tot[tk]:+.2f}   rank #{rank[tk]} of {len(df)}")
        print()


if __name__ == "__main__":
    main()
