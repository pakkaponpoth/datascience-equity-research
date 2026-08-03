"""Does the aggressive edge survive trading costs?  (the honest stress test)

Yearly rebalance per profile; each year we compute TURNOVER (how much of the
book we swap) and subtract real Thai round-trip costs. Reports gross vs net
return over the last 10 years, plus average turnover (momentum should trade
most). If aggressive still beats buy-and-hold after costs, the edge is real-ish.
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
# Thai retail round-trip cost scenarios (buy+sell): commission+VAT ~0.34%, +slippage
COSTS = {"0.5% round-trip": 0.005, "1.0% round-trip": 0.010}

print(f"{len(tickers)} tickers - fetching MAX monthly...")
mpx = yf.download(tickers, period="max", interval="1mo", auto_adjust=True, progress=False)["Close"].dropna(how="all")
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


gross = {p: [] for p in PROFILES}
turn = {p: [] for p in PROFILES}
prev = {p: set() for p in PROFILES}
byear = []
i = 12
while i + 12 < len(mpx):
    adj = adj_month(i)
    if adj is None:
        i += 12; continue
    fwd = mpx.iloc[i + 12] / mpx.iloc[i] - 1
    byear.append(float(fwd[adj.index].dropna().mean()))
    for p, W in PROFILES.items():
        sc = sum(W[f] * adj[f] for f in FACT).rank(pct=True)
        picks = set(sc[sc >= sc.quantile(0.80)].index)
        gross[p].append(float(fwd[list(picks)].dropna().mean()))
        n = len(picks)
        to = 1.0 if not prev[p] else len(picks - prev[p]) / n     # fraction swapped
        turn[p].append(to)
        prev[p] = picks
    i += 12

cum = lambda xs: float(np.prod([1 + x for x in xs]) - 1)
L = 10                                                            # last 10 yearly rebalances
print(f"\nLast {L} yearly rebalances · buy&hold(10y) = {cum(byear[-L:])*100:+.0f}%\n")
print(f"{'profile':<13}{'avg turnover':>13}{'gross 10y':>11}", end="")
for c in COSTS:
    print(f"{'net@'+c.split()[0]:>13}", end="")
print()
for p in PROFILES:
    g10 = gross[p][-L:]; t10 = turn[p][-L:]
    print(f"{p:<13}{np.mean(t10)*100:>11.0f}%{cum(g10)*100:>10.0f}%", end="")
    for c, rt in COSTS.items():
        net = [g - to * rt for g, to in zip(g10, t10)]
        print(f"{cum(net)*100:>12.0f}%", end="")
    print()
print("\n(turnover = % of the book swapped each year · momentum trades most · "
      "survivorship-biased, read relatively)")
