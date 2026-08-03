"""Long-horizon backtest — 5-year and 10-year returns per profile.

Yearly rebalance (buy each profile's top-20%, hold 12 months, compound), over
the longest history available. Reports cumulative return for the last 5y, last
10y, and full window, vs buy-and-hold. NOTE two honest limits: many Thai names
lack long history (dropped early), and the universe = today's SURVIVORS
(survivorship bias inflates old returns). Read as illustrative, not exact.
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

print(f"{len(tickers)} tickers - fetching MAX monthly history...")
mpx = yf.download(tickers, period="max", interval="1mo", auto_adjust=True, progress=False)["Close"]
mpx = mpx.dropna(how="all")
rets = mpx.pct_change(fill_method=None)
print(f"history: {mpx.index.min().date()} -> {mpx.index.max().date()} ({len(mpx)} months)")


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


# non-overlapping yearly rebalances (buy, hold 12m, compound)
yearly = {p: [] for p in PROFILES}
byear = []
dates = []
i = 12
while i + 12 < len(mpx):
    adj = adj_month(i)
    if adj is None:
        i += 12; continue
    fwd = mpx.iloc[i + 12] / mpx.iloc[i] - 1
    idx = adj.index
    byear.append(float(fwd[idx].dropna().mean()))
    dates.append(mpx.index[i].date())
    for p, W in PROFILES.items():
        sc = sum(W[f] * adj[f] for f in FACT).rank(pct=True)
        picks = sc[sc >= sc.quantile(0.80)].index
        yearly[p].append(float(fwd[picks].dropna().mean()))
    i += 12

n = len(byear)
print(f"\n{n} yearly rebalances: {dates[0]} -> {dates[-1]}\n")


def cum(xs):
    return float(np.prod([1 + x for x in xs]) - 1)


def cagr(xs):
    return (1 + cum(xs)) ** (1 / len(xs)) - 1 if xs else float("nan")


print(f"{'profile':<14}{'last 5y':>10}{'last 10y':>11}{'full':>10}{'CAGR':>9}")
for p in PROFILES:
    ys = yearly[p]
    l5 = cum(ys[-5:]) if len(ys) >= 5 else float("nan")
    l10 = cum(ys[-10:]) if len(ys) >= 10 else cum(ys)
    print(f"{p:<14}{l5*100:>9.0f}%{l10*100:>10.0f}%{cum(ys)*100:>9.0f}%{cagr(ys)*100:>+8.1f}%")
b5 = cum(byear[-5:]) if n >= 5 else float("nan")
b10 = cum(byear[-10:]) if n >= 10 else cum(byear)
print(f"{'buy & hold':<14}{b5*100:>9.0f}%{b10*100:>10.0f}%{cum(byear)*100:>9.0f}%{cagr(byear)*100:>+8.1f}%")
print("\n(cumulative % over the window · CAGR = annual growth rate · survivorship-biased)")
