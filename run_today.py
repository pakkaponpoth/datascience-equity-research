"""SETScout engine — run once/day to refresh today.json with REAL data.

    python run_today.py

Reads the universe (tickers + Thai names + sectors) from today.json, pulls
real prices from Yahoo Finance, scores every stock with a multi-factor
filter, and writes today.json back. The website just reads that file.

v1 factors are PRICE-BASED proxies (honest, always available):
  momentum = 6-month return · growth = 12-month return ·
  value = cheapness vs 200-day avg · quality = low volatility ·
  health = small max-drawdown.
v2 upgrade = real fundamentals (P/E, ROE, earnings growth).

Scoring (less biased): each factor is winsorized + z-scored, then
SECTOR-NEUTRALIZED — a stock is judged against its SECTOR PEERS, not the whole
market — so one low-vol sector (e.g. banks) can no longer dominate the top.
Composite = weighted z-score; final score = its percentile across the market.
Factor WEIGHTS below are placeholders until the AHP expert survey sets them.
"""
import json, os
import numpy as np, pandas as pd, yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "today.json")
W = {"quality": 0.28, "value": 0.24, "momentum": 0.20, "health": 0.16, "growth": 0.12}


def main():
    uni = json.load(open(FILE, encoding="utf-8"))
    meta = {s["ticker"]: {"name": s["name"], "name_th": s["name_th"],
                          "sector": s["sector"]} for s in uni["stocks"]}
    tickers = list(meta)
    print(f"{len(tickers)} tickers - fetching ~2y prices...")
    px = yf.download(tickers, period="2y", auto_adjust=True, progress=False)["Close"]
    px = px.dropna(how="all")

    rows = {}
    for t in tickers:
        s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
        if len(s) < 130:
            continue
        ret6 = s.iloc[-1] / s.iloc[-126] - 1
        ret12 = s.iloc[-1] / s.iloc[max(0, len(s) - 252)] - 1
        cheap = -(s.iloc[-1] / s.tail(200).mean() - 1)
        dvol = s.pct_change().tail(252).std()
        eq = s.tail(252)
        mdd = (eq / eq.cummax() - 1).min()
        rows[t] = dict(momentum=ret6, growth=ret12, value=cheap,
                       quality=-dvol * np.sqrt(252), health=mdd,
                       last=round(float(s.iloc[-1]), 2),
                       chg=round(float(s.pct_change().iloc[-1] * 100), 1), dvol=dvol)
    df = pd.DataFrame(rows).T
    FACTORS = ["momentum", "growth", "value", "quality", "health"]
    df["sector"] = [meta[t]["sector"] for t in df.index]

    # 1. winsorized z-score each factor across the universe (robust, avoids ties)
    def zscore(s):
        s = s.astype(float); sd = s.std(ddof=0)
        return ((s - s.mean()) / (sd if sd > 0 else 1.0)).clip(-3, 3)
    for f in FACTORS:
        df[f + "_z"] = zscore(df[f])

    # 2. SECTOR-NEUTRALIZE: subtract each factor's sector mean, so a stock is
    #    scored vs its sector PEERS (kills the "banks are low-vol -> banks win"
    #    bias). Only for sectors with >=3 names; tiny sectors keep the market z.
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    in_big = df["sector"].isin(big)
    for f in FACTORS:
        smean = df.groupby("sector")[f + "_z"].transform("mean")
        df[f + "_adj"] = df[f + "_z"] - smean.where(in_big, 0.0)

    # 3. composite = weighted sum of sector-adjusted z-scores
    df["composite"] = sum(W[f] * df[f + "_adj"] for f in FACTORS)
    # 4. final score = percentile of the composite (0-1, well spread)
    df["score01"] = df["composite"].rank(pct=True)

    stocks = []
    for t, r in df.iterrows():
        s01 = float(r["score01"])
        # verdict by percentile band: top 20% BUY, next 35% WAIT, rest AVOID
        verdict = "BUY" if s01 >= 0.80 else "WAIT" if s01 >= 0.45 else "AVOID"
        var_m = 1.645 * r["dvol"] * np.sqrt(21)
        risk = -int(round(min(max(var_m * 100, 6), 35)))
        mw = round(float(min(0.40, max(0.08, 0.42 * (1 - abs(risk) / 32)))), 2)
        # reasons = the sector-adjusted factors that set it apart from its peers
        adjv = {f: r[f + "_adj"] for f in FACTORS}
        keys = sorted(adjv, key=lambda k: adjv[k], reverse=True)
        because = [keys[0] + ":pos", keys[1] + ":pos"] if verdict == "BUY" \
            else [keys[0] + ":pos", keys[-1] + ":neg"]
        m = meta[t]
        stocks.append(dict(ticker=t, name=m["name"], name_th=m["name_th"],
            sector=m["sector"], score=round(s01, 2), verdict=verdict,
            risk_month_pct=risk, max_weight=mw, p_win=round(0.44 + s01 * 0.22, 2),
            because=because, last=r["last"], chg_pct=r["chg"]))
    stocks.sort(key=lambda s: s["score"], reverse=True)

    out = {"generated": str(pd.Timestamp.today().date()), "universe": uni["universe"],
           "disclaimer": uni["disclaimer"], "stocks": stocks}
    json.dump(out, open(FILE, "w", encoding="utf-8"), ensure_ascii=False)
    n = {v: sum(s["verdict"] == v for s in stocks) for v in ("BUY", "WAIT", "AVOID")}
    print(f"wrote {len(stocks)} stocks -> today.json  "
          f"(BUY {n['BUY']} / WAIT {n['WAIT']} / AVOID {n['AVOID']})")


if __name__ == "__main__":
    main()
