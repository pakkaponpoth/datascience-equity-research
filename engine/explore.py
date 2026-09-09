"""Period explorer - pick any stretch of years and see what really happened.

    python explore.py                 # interactive: type periods, see results
    python explore.py 2005 2007       # one period
    python explore.py --years         # every single year, one row each

WHY THIS EXISTS
---------------
The blind test printed "+60.2% over 12 months" for the balanced profile, which is
not believable. Two separate things were wrong with that number, and this tool
shows BOTH of them on every run so they stop being abstract:

1. "Average of 12-month returns" is not "how fast your money grew". Averaging
   overlapping one-year windows inflates the figure. This tool prints the average
   AND the compounded rate side by side, so you can watch them disagree.

2. Our stock list only contains companies that still exist in 2026. Going back in
   time, more and more of them had not listed yet - and the ones that had are the
   survivors. So the tool prints how many stocks actually existed in each period,
   and puts the REAL SET index next to our result. The gap between "buy & hold"
   and "REAL SET index" is roughly the size of the bias, in that period.

Read it this way: compare rows WITHIN a period. Never quote a number on its own.

First run downloads ~95 tickers (about 30s) and caches to .price_cache.csv.
Delete that file to force a fresh download.
"""
import os
import sys

import numpy as np
import pandas as pd
import yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".price_cache.csv")
IDX_CACHE = os.path.join(HERE, ".index_cache.csv")
FACT = ["momentum", "growth", "value", "quality", "health"]
PROFILES = {                                    # FROZEN - same as run_today.py
    "conservative": {"quality": .40, "health": .30, "value": .20, "momentum": .05, "growth": .05},
    "balanced":     {"quality": .28, "value": .24, "momentum": .20, "health": .16, "growth": .12},
    "aggressive":   {"momentum": .40, "growth": .30, "value": .15, "quality": .10, "health": .05},
}
H = 12


def load():
    """Monthly prices for the universe + the real SET index. Cached to disk."""
    import json
    uni = json.load(open(os.path.join(HERE, "universe.json"), encoding="utf-8"))
    meta = {s["ticker"]: s["sector"] for s in uni["stocks"]}

    if os.path.exists(CACHE):
        mpx = pd.read_csv(CACHE, index_col=0, parse_dates=True)
    else:
        print(f"downloading {len(meta)} tickers (one time, ~30s)...")
        px = yf.download(list(meta), period="max", auto_adjust=True,
                         progress=False)["Close"].dropna(how="all")
        mpx = px.resample("ME").last()
        mpx.to_csv(CACHE)
        print(f"cached to {os.path.basename(CACHE)}")

    if os.path.exists(IDX_CACHE):
        idx = pd.read_csv(IDX_CACHE, index_col=0, parse_dates=True).iloc[:, 0]
    else:
        print("downloading the real SET index...")
        raw = yf.Ticker("^SET.BK").history(period="max", auto_adjust=False)["Close"]
        idx = raw.resample("ME").last().dropna()
        idx.index = idx.index.tz_localize(None)
        idx.to_frame("SET").to_csv(IDX_CACHE)
    return mpx, meta, idx


def adj_month(mpx, rets, meta, i):
    """Sector-neutral factor scores using only data up to month i."""
    hp, hr = mpx.iloc[:i + 1], rets.iloc[:i + 1]
    rows = {}
    for t in mpx.columns:
        s = hp[t].dropna()
        if len(s) < 13:
            continue
        r12 = hr[t].dropna().iloc[-12:]
        if len(r12) < 12:
            continue
        eq = s.iloc[-12:]
        rows[t] = dict(momentum=s.iloc[-1] / s.iloc[-7] - 1, growth=s.iloc[-1] / s.iloc[-13] - 1,
                       value=-(s.iloc[-1] / s.iloc[-11:].mean() - 1),
                       quality=-r12.std() * np.sqrt(12),
                       health=(eq / eq.cummax() - 1).min(), sector=meta[t])
    if len(rows) < 10:
        return None
    df = pd.DataFrame(rows).T
    for f in FACT:
        c = df[f].astype(float)
        sd = c.std(ddof=0)
        df[f] = ((c - c.mean()) / (sd if sd > 0 else 1)).clip(-3, 3)
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    inb = df["sector"].isin(big)
    for f in FACT:
        df[f] = df[f] - df.groupby("sector")[f].transform("mean").where(inb, 0.0)
    return df


def period(mpx, rets, meta, idx, y0, y1, quiet=False):
    lo = pd.Timestamp(f"{y0}-01-01")
    hi = pd.Timestamp(f"{y1}-12-31")
    got = {p: [] for p in PROFILES}
    bench, cover = [], []
    for i in range(12, len(mpx) - H):
        d = mpx.index[i]
        if not (lo <= d <= hi):
            continue
        adj = adj_month(mpx, rets, meta, i)
        if adj is None:
            continue
        hold = rets.iloc[i + 1:i + 1 + H]
        cover.append(len(adj.index))
        bench.append((1 + hold[adj.index].mean(axis=1)).prod() - 1)
        for p, W in PROFILES.items():
            sc = sum(W[f] * adj[f] for f in FACT).rank(pct=True)
            picks = sc[sc >= sc.quantile(0.80)].index
            got[p].append((1 + hold[picks].mean(axis=1)).prod() - 1)

    if not bench:
        print(f"  {y0}-{y1}: not enough data")
        return None

    # compounded: actually hold the equal-weight basket across the whole period
    m = rets.loc[(rets.index >= lo) & (rets.index <= hi)]
    live = [t for t in m.columns if m[t].notna().sum() > len(m) * 0.5]
    yrs = len(m) / 12
    comp = lambda s: (1 + s).prod() ** (1 / yrs) - 1 if yrs > 0 else float("nan")
    bench_comp = comp(m[live].mean(axis=1))

    # the real index over the same window
    iw = idx.loc[(idx.index >= lo) & (idx.index <= hi)]
    # 12 monthly points span 11 intervals - use len-1 or a single year reads as nan
    idx_cagr = ((iw.iloc[-1] / iw.iloc[0]) ** (12 / (len(iw) - 1)) - 1
                if len(iw) >= 3 else float("nan"))

    n = int(np.median(cover))
    gap = (bench_comp - idx_cagr) * 100
    res = dict(n=n, bench_avg=float(np.mean(bench)), bench_comp=float(bench_comp),
               idx=float(idx_cagr), gap=float(gap),
               **{p: float(np.mean(got[p])) for p in PROFILES})
    if quiet:
        return res

    print(f"\n=== {y0}-{y1} ===")
    print(f"stocks that existed then: {n} of {len(meta)}  "
          f"({100*n/len(meta):.0f}% - the rest had not listed yet)")
    print("\nWHAT ACTUALLY HAPPENED (compounded, per year):")
    print(f"   our stock list, equal weight : {bench_comp*100:>7.1f}%")
    print(f"   the REAL SET index           : {idx_cagr*100:>7.1f}%")
    print(f"   difference                   : {gap:>+7.1f}   <- this is the bias")
    print("\nHOW THE PROFILES COMPARED (avg of 12-month returns):")
    for p in PROFILES:
        print(f"   {p:<13}{np.mean(got[p])*100:>17.1f}%")
    print(f"   {'buy & hold':<13}{np.mean(bench)*100:>17.1f}%")
    print("   ^ use these to COMPARE rows only. Do not quote them as returns.")
    return res


def main():
    mpx, meta, idx = load()
    rets = mpx.pct_change(fill_method=None)
    print(f"history: {mpx.index[0].date()} -> {mpx.index[-1].date()}")

    args = sys.argv[1:]
    if args and args[0] == "--years":
        print("\nOne row per starting year. 'avg 12mo' is the misleading number;")
        print("'index' is what the Thai market actually did that year.\n")
        print(f"{'year':<7}{'stocks':>7}{'balanced':>10}{'aggr':>8}"
              f"{'buy&hold':>10}{'REALindex':>11}{'gap':>8}")
        for y in range(1999, 2025):
            r = period(mpx, rets, meta, idx, y, y, quiet=True)
            if r:
                print(f"{y:<7}{r['n']:>7}{r['balanced']*100:>9.0f}%{r['aggressive']*100:>7.0f}%"
                      f"{r['bench_avg']*100:>9.0f}%{r['idx']*100:>10.0f}%{r['gap']:>+8.0f}")
        return

    if len(args) == 2:
        period(mpx, rets, meta, idx, int(args[0]), int(args[1]))
        return

    print("\nType two years, e.g.  2005 2007   (blank line or 'q' to quit)")
    while True:
        try:
            raw = input("\nperiod> ").strip()
        except EOFError:
            break
        if not raw or raw.lower() in ("q", "quit", "exit"):
            break
        parts = raw.replace("-", " ").split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("  give me two years, like: 2005 2007")
            continue
        period(mpx, rets, meta, idx, int(parts[0]), int(parts[1]))


if __name__ == "__main__":
    main()
