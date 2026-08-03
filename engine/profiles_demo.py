"""Do different risk-profiles really produce different picks? — proof of concept.

Same factors, three WEIGHT sets (= three engines for three risk-aversion levels).
Shows each profile's top picks + the average risk of its picks. If the
conservative list is genuinely lower-risk and the aggressive list higher-risk,
the multi-engine idea is real.
"""
import json, os
import numpy as np, pandas as pd, yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
uni = json.load(open(os.path.join(HERE, "today.json"), encoding="utf-8"))
meta = {s["ticker"]: {"name": s["name"], "sector": s["sector"]} for s in uni["stocks"]}
tickers = list(meta)
FACT = ["momentum", "growth", "value", "quality", "health"]

PROFILES = {
    "Conservative": {"quality": .40, "health": .30, "value": .20, "momentum": .05, "growth": .05},
    "Balanced":     {"quality": .25, "value": .25, "momentum": .20, "health": .15, "growth": .15},
    "Aggressive":   {"momentum": .40, "growth": .30, "value": .15, "quality": .10, "health": .05},
}

print(f"{len(tickers)} tickers - fetching ~2y prices...")
px = yf.download(tickers, period="2y", auto_adjust=True, progress=False)["Close"].dropna(how="all")

rows = {}
for t in tickers:
    s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
    if len(s) < 130:
        continue
    dvol = s.pct_change().tail(252).std()
    eq = s.tail(252)
    rows[t] = dict(momentum=s.iloc[-1] / s.iloc[-126] - 1, growth=s.iloc[-1] / s.iloc[max(0, len(s)-252)] - 1,
                   value=-(s.iloc[-1] / s.tail(200).mean() - 1), quality=-dvol*np.sqrt(252),
                   health=(eq/eq.cummax()-1).min(), sector=meta[t]["sector"],
                   risk=-int(round(min(max(1.645*dvol*np.sqrt(21)*100, 6), 35))))
df = pd.DataFrame(rows).T

# z-score + sector-neutralize (same as the real engine)
for f in FACT:
    c = df[f].astype(float); sd = c.std(ddof=0)
    df[f + "z"] = ((c - c.mean()) / (sd if sd > 0 else 1)).clip(-3, 3)
big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
inb = df["sector"].isin(big)
for f in FACT:
    df[f + "z"] = df[f + "z"] - df.groupby("sector")[f + "z"].transform("mean").where(inb, 0.0)

for name, W in PROFILES.items():
    df["sc"] = sum(W[f] * df[f + "z"] for f in FACT)
    top = df.sort_values("sc", ascending=False).head(int(len(df) * 0.20))
    picks5 = df.sort_values("sc", ascending=False).head(5)
    avg_risk = top["risk"].mean()
    avg_mom = top["momentum"].astype(float).mean()
    print(f"\n=== {name} ===")
    print(f"  top 5: {', '.join(t.replace('.BK','') for t in picks5.index)}")
    print(f"  avg risk of picks (monthly VaR): {avg_risk:.0f}%   "
          f"avg 6mo momentum: {avg_mom*100:+.0f}%")

# overlap between conservative and aggressive top-20%
c = set(df.assign(sc=sum(PROFILES['Conservative'][f]*df[f+'z'] for f in FACT))
          .sort_values('sc', ascending=False).head(int(len(df)*.2)).index)
a = set(df.assign(sc=sum(PROFILES['Aggressive'][f]*df[f+'z'] for f in FACT))
          .sort_values('sc', ascending=False).head(int(len(df)*.2)).index)
print(f"\nOverlap Conservative vs Aggressive top-20%: {len(c&a)}/{len(c)} stocks "
      f"({'genuinely different lists' if len(c&a) < len(c)*0.5 else 'too similar'})")
