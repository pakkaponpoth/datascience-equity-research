"""Backtest all 3 risk profiles side by side (1-year hold, point-in-time).

Same sector-neutral factors (computed once per month), then each profile's
weights pick its own top-20%. We hold 12 months and measure BOTH return and
the volatility you'd have lived through. Answers: do the profiles actually
differ on return + risk, and does either beat buy-and-hold?
"""
import json, os
import numpy as np, pandas as pd, yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
uni = json.load(open(os.path.join(HERE, "today.json"), encoding="utf-8"))
meta = {s["ticker"]: s["sector"] for s in uni["stocks"]}
tickers = list(meta)
FACT = ["momentum", "growth", "value", "quality", "health"]
PROFILES = {
    "conservative": {"quality": .40, "health": .30, "value": .20, "momentum": .05, "growth": .05},
    "balanced":     {"quality": .28, "value": .24, "momentum": .20, "health": .16, "growth": .12},
    "aggressive":   {"momentum": .40, "growth": .30, "value": .15, "quality": .10, "health": .05},
}
H, K = 12, 200
np.random.seed(7)

print(f"{len(tickers)} tickers - fetching ~8y monthly prices...")
px = yf.download(tickers, period="8y", auto_adjust=True, progress=False)["Close"].dropna(how="all")
mpx = px.resample("ME").last()
rets = mpx.pct_change(fill_method=None)


def adj_month(i):
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
        df[f] = ((c - c.mean()) / (sd if sd > 0 else 1)).clip(-3, 3)
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    inb = df["sector"].isin(big)
    for f in FACT:
        df[f] = df[f] - df.groupby("sector")[f].transform("mean").where(inb, 0.0)
    return df


res = {p: {"ret": [], "vol": [], "rand": [[] for _ in range(K)]} for p in PROFILES}
bench = []
for i in range(12, len(mpx) - H):
    adj = adj_month(i)
    if adj is None:
        continue
    hold = rets.iloc[i + 1:i + 1 + H]            # 12 monthly returns AFTER i (no look-ahead)
    idx = adj.index
    bench.append((1 + hold[idx].mean(axis=1)).prod() - 1)
    pool = list(idx)
    for p, W in PROFILES.items():
        sc = sum(W[f] * adj[f] for f in FACT).rank(pct=True)
        picks = sc[sc >= sc.quantile(0.80)].index
        pm = hold[picks].mean(axis=1)            # equal-weight monthly returns of the picks
        res[p]["ret"].append((1 + pm).prod() - 1)
        res[p]["vol"].append(pm.std() * np.sqrt(12))
    n = len(picks)
    for k in range(K):
        rp = np.random.choice(pool, min(n, len(pool)), replace=False)
        rr = (1 + hold[rp].mean(axis=1)).prod() - 1
        for p in PROFILES:
            res[p]["rand"][k].append(rr)

b_avg = np.mean(bench)
print(f"\nfair test: BUY the top picks, HOLD {H} months  ({len(bench)} start-points)")
print(f"buy & hold (whole universe): {b_avg*100:+.1f}% avg\n")
print(f"{'profile':<14}{'avg 12mo ret':>13}{'avg risk(vol)':>14}{'ret/risk':>9}{'vs B&H':>9}{'luck bar':>10}")
for p in PROFILES:
    r = np.mean(res[p]["ret"]); v = np.mean(res[p]["vol"])
    rand_avg = sorted(np.mean(x) for x in res[p]["rand"])
    luck = 100 * sum(1 for x in rand_avg if x < r) / K
    print(f"{p:<14}{r*100:>12.1f}%{v*100:>13.1f}%{r/v:>9.2f}{(r-b_avg)*100:>+8.1f}{luck:>8.0f}%")
print("\nread: higher risk(vol) = bumpier ride · ret/risk = return per unit of risk")
