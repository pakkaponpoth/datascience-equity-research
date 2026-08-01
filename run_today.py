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
    for f in ["momentum", "growth", "value", "quality", "health"]:
        df[f] = df[f].rank(pct=True)

    stocks = []
    for t, r in df.iterrows():
        score = round(sum(W[f] * r[f] for f in W), 2)
        verdict = "BUY" if score >= 0.62 else "WAIT" if score >= 0.48 else "AVOID"
        var_m = 1.645 * r["dvol"] * np.sqrt(21)
        risk = -int(round(min(max(var_m * 100, 6), 35)))
        mw = round(float(min(0.40, max(0.08, 0.42 * (1 - abs(risk) / 32)))), 2)
        keys = sorted(W, key=lambda k: r[k], reverse=True)
        because = [keys[0] + ":pos", keys[1] + ":pos"] if verdict == "BUY" \
            else [keys[0] + ":pos", keys[-1] + ":neg"]
        m = meta[t]
        stocks.append(dict(ticker=t, name=m["name"], name_th=m["name_th"],
            sector=m["sector"], score=score, verdict=verdict,
            risk_month_pct=risk, max_weight=mw, p_win=round(0.44 + score * 0.22, 2),
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
