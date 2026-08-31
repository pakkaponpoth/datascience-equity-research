"""SETScout HOLD backtest — the fair test.

    python backtest_hold.py

Same point-in-time scoring as backtest.py, but instead of churning monthly it
does what real users do: BUY the top picks and HOLD for H months. For each
start month it measures the H-month forward return of the picks vs the whole
universe (buy-and-hold proxy), plus a luck bar (random portfolios held the
same way). Runs H = 6 and 12 months. No look-ahead.
"""
import json, os
import numpy as np, pandas as pd, yfinance as yf
from reportlib import capture, load_universe

capture("backtest_hold", "Hold test - buy the picks and hold (the fair test)",
        {"rebalance": "none - buy and hold", "horizons": "6 and 12 months", "history": "~8y monthly", "why": "matches how users actually behave, not monthly churn"})

HERE = os.path.dirname(os.path.abspath(__file__))
meta, _uni_src = load_universe()
tickers = list(meta)
print(f"universe: {len(tickers)} tickers from {_uni_src}")
W = {"quality": 0.28, "value": 0.24, "momentum": 0.20, "health": 0.16, "growth": 0.12}
FACT = ["momentum", "growth", "value", "quality", "health"]
K = 300
np.random.seed(7)

print(f"{len(tickers)} tickers - fetching ~8y monthly prices...")
px = yf.download(tickers, period="8y", auto_adjust=True, progress=False)["Close"].dropna(how="all")
mpx = px.resample("ME").last()
rets = mpx.pct_change(fill_method=None)


def score_month(i):
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
                       value=-(s.iloc[-1] / s.iloc[-11:].mean() - 1), quality=-r12.std() * np.sqrt(12),
                       health=(eq / eq.cummax() - 1).min(), sector=meta[t])
    if len(rows) < 10:
        return None
    df = pd.DataFrame(rows).T
    for f in FACT:
        c = df[f].astype(float); sd = c.std(ddof=0)
        df[f] = ((c - c.mean()) / (sd if sd > 0 else 1.0)).clip(-3, 3)
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    inb = df["sector"].isin(big)
    for f in FACT:
        df[f] = df[f] - df.groupby("sector")[f].transform("mean").where(inb, 0.0)
    return (sum(W[f] * df[f] for f in FACT)).rank(pct=True)


for H in (6, 12):
    strat, bench, rand, calib = [], [], [[] for _ in range(K)], []
    for i in range(12, len(mpx) - H):
        sc = score_month(i)
        if sc is None:
            continue
        fwd = mpx.iloc[i + H] / mpx.iloc[i] - 1          # H-month HOLD return, no look-ahead
        picks = sc[sc >= sc.quantile(0.80)].index
        pr = fwd[picks].dropna()
        if len(pr) == 0:
            continue
        strat.append(pr.mean())
        bench.append(fwd[sc.index].dropna().mean())
        pool, n = list(sc.index), len(picks)
        for k in range(K):
            rp = np.random.choice(pool, min(n, len(pool)), replace=False)
            rr = fwd[rp].dropna()
            rand[k].append(rr.mean() if len(rr) else 0.0)
        for t in sc.index:
            f = fwd.get(t)
            if pd.notna(f):
                calib.append((float(sc[t]), 1 if f > 0 else 0))

    s_avg, b_avg = np.mean(strat), np.mean(bench)
    rand_avg = sorted(np.mean(r) for r in rand)
    luck = 100 * sum(1 for r in rand_avg if r < s_avg) / K
    hit = 100 * sum(1 for x in strat if x > 0) / len(strat)
    print(f"\n=== HOLD {H} months  ({len(strat)} start-points) ===")
    print(f"picks avg {H}-mo return : {s_avg*100:+.1f}%")
    print(f"buy & hold avg          : {b_avg*100:+.1f}%")
    print(f"vs B&H                  : {(s_avg-b_avg)*100:+.1f} pts  -> "
          f"{'BEATS' if s_avg>b_avg else 'trails'}")
    print(f"picks up after {H}mo     : {hit:.0f}%")
    print(f"LUCK BAR: beat {luck:.0f}% of {K} random books  -> "
          f"{'edge looks real' if luck>=90 else 'within luck' if luck<75 else 'borderline'}")
    cal = pd.DataFrame(calib, columns=["score", "win"])
    cal["b"] = (cal["score"] * 5).clip(0, 4).astype(int)     # quintiles
    t = cal.groupby("b")["win"].mean()
    print("  up-rate by score quintile (low->high): " +
          "  ".join(f"{v*100:.0f}%" for v in t))
