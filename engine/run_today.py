"""SETScout engine — run once/day to refresh today.json with REAL data.

    python run_today.py

Reads the universe (tickers + Thai names + sectors) from universe.json, pulls
real prices from Yahoo Finance, scores every stock with a multi-factor
filter, and writes today.json. The website just reads that file.

universe.json is READ-ONLY here and today.json is WRITE-ONLY. That separation
matters: the engine used to read its own output, so any ticker that failed to
fetch once vanished from the universe forever (4 were lost that way). Now a
failed fetch is skipped for one run and retried the next day.

p_win is the MEASURED up-rate for the stock's score decile, read from
calibration.json (written by backtest.py). It is flat at roughly 47% across
every decile - the score does not predict direction - and the app must say so.
If calibration.json is missing, p_win is emitted as null rather than invented.

v1 factors are PRICE-BASED proxies (honest, always available):
  momentum = 6-month return · growth = 12-month return ·
  value = cheapness vs 200-day avg · quality = low volatility ·
  health = small max-drawdown.
v2 upgrade = real fundamentals (P/E, ROE, earnings growth).

Scoring (less biased): each factor is winsorized + z-scored, then
SECTOR-NEUTRALIZED — a stock is judged against its SECTOR PEERS, not the whole
market — so one low-vol sector (e.g. banks) can no longer dominate the top.
Composite = weighted z-score; final score = its percentile across the market.

PERSONALIZATION: the same factors are combined with THREE weight sets, one per
risk profile, so the website's risk quiz can serve a matching list:
  conservative -> safety factors ·  balanced -> even ·  aggressive -> momentum.
Factor WEIGHTS are placeholders until the AHP expert survey sets them.
"""
import json, os
import numpy as np, pandas as pd, yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "today.json")          # OUTPUT only - never read as input
UNIVERSE_FILE = os.path.join(HERE, "universe.json")   # INPUT - the canonical stock list
CAL_FILE = os.path.join(HERE, "calibration.json")     # INPUT - measured up-rate per decile
FACTORS = ["momentum", "growth", "value", "quality", "health"]


def load_universe():
    """Canonical ticker list. Read-only, so a failed fetch can never shrink it.

    Falls back to today.json for old checkouts that predate universe.json.
    """
    try:
        return json.load(open(UNIVERSE_FILE, encoding="utf-8")), True
    except OSError:
        print("WARNING: universe.json missing - falling back to today.json.\n"
              "         Any ticker that fails to fetch will be lost permanently.")
        return json.load(open(FILE, encoding="utf-8")), False


def load_calibration():
    """Real backtested up-rate per score decile, written by backtest.py.

    Returns (by_decile, meta) or (None, None) when it has not been measured.
    """
    try:
        c = json.load(open(CAL_FILE, encoding="utf-8"))
        by = {int(k): float(v) for k, v in c["by_decile"].items()}
        vals = list(by.values())
        meta = {"source": "backtest.py", "months": c.get("months"),
                "generated": c.get("generated"),
                "base_rate": round(sum(vals) / len(vals), 3),
                "min": round(min(vals), 3), "max": round(max(vals), 3),
                "spread_pp": round((max(vals) - min(vals)) * 100, 1),
                "note": "Measured share of stocks in each score decile that rose the "
                        "following month. Flat across deciles: the score does not "
                        "predict direction. Not a forecast."}
        return by, meta
    except (OSError, KeyError, ValueError, ZeroDivisionError):
        return None, None


def p_win_for(s01, calib):
    """Measured up-rate for this score's decile - or None if never measured.

    Deliberately NOT derived from the score. The old placeholder was
    0.44 + 0.22*s01, which climbed with rank; backtest.py shows the real
    up-rate is flat (~47%) across every decile, so that shape was false.
    Bucketing matches backtest.py exactly: (score*10).clip(0, 9).
    """
    if not calib:
        return None
    return round(calib[min(9, max(0, int(s01 * 10)))], 3)

# one weight set per risk profile (AHP survey will replace these numbers)
PROFILES = {
    "conservative": {"quality": .40, "health": .30, "value": .20, "momentum": .05, "growth": .05},
    "balanced":     {"quality": .28, "value": .24, "momentum": .20, "health": .16, "growth": .12},
    "aggressive":   {"momentum": .40, "growth": .30, "value": .15, "quality": .10, "health": .05},
}


def main():
    uni, from_universe_file = load_universe()
    calib, cal_meta = load_calibration()
    meta = {s["ticker"]: {"name": s["name"], "name_th": s["name_th"],
                          "sector": s["sector"]} for s in uni["stocks"]}
    tickers = list(meta)
    src = "universe.json" if from_universe_file else "today.json (fallback)"
    print(f"{len(tickers)} tickers from {src} - fetching ~2y prices...")
    print("p_win: " + (f"CALIBRATED from calibration.json "
                       f"({cal_meta['months']} months, base rate "
                       f"{cal_meta['base_rate']*100:.1f}%)" if calib else
                       "NOT AVAILABLE - will be emitted as null (run backtest.py first)"))
    px = yf.download(tickers, period="2y", auto_adjust=True, progress=False)["Close"]
    px = px.dropna(how="all")

    rows = {}
    for t in tickers:
        s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
        if len(s) < 130:
            continue
        rows[t] = dict(
            momentum=s.iloc[-1] / s.iloc[-126] - 1,
            growth=s.iloc[-1] / s.iloc[max(0, len(s) - 252)] - 1,
            value=-(s.iloc[-1] / s.tail(200).mean() - 1),
            quality=-s.pct_change().tail(252).std() * np.sqrt(252),
            health=(s.tail(252) / s.tail(252).cummax() - 1).min(),
            last=round(float(s.iloc[-1]), 2),
            chg=round(float(s.pct_change().iloc[-1] * 100), 1),
            dvol=s.pct_change().tail(252).std())
    df = pd.DataFrame(rows).T
    df["sector"] = [meta[t]["sector"] for t in df.index]

    # winsorized z-score, then sector-neutralize (judge vs sector peers)
    def z(c):
        c = c.astype(float); sd = c.std(ddof=0)
        return ((c - c.mean()) / (sd if sd > 0 else 1.0)).clip(-3, 3)
    for f in FACTORS:
        df[f + "_z"] = z(df[f])
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    in_big = df["sector"].isin(big)
    for f in FACTORS:
        smean = df.groupby("sector")[f + "_z"].transform("mean")
        df[f + "_adj"] = df[f + "_z"] - smean.where(in_big, 0.0)

    def build_list(W):
        score01 = sum(W[f] * df[f + "_adj"] for f in FACTORS).rank(pct=True)
        out = []
        for t in df.index:
            r = df.loc[t]; s01 = float(score01[t])
            verdict = "BUY" if s01 >= 0.80 else "WAIT" if s01 >= 0.45 else "AVOID"
            risk = -int(round(min(max(1.645 * r["dvol"] * np.sqrt(21) * 100, 6), 35)))
            mw = round(float(min(0.40, max(0.08, 0.42 * (1 - abs(risk) / 32)))), 2)
            adjv = {f: r[f + "_adj"] for f in FACTORS}
            keys = sorted(adjv, key=lambda k: adjv[k], reverse=True)
            because = [keys[0] + ":pos", keys[1] + ":pos"] if verdict == "BUY" \
                else [keys[0] + ":pos", keys[-1] + ":neg"]
            m = meta[t]
            out.append(dict(ticker=t, name=m["name"], name_th=m["name_th"],
                sector=m["sector"], score=round(s01, 2), verdict=verdict,
                risk_month_pct=risk, max_weight=mw, p_win=p_win_for(s01, calib),
                because=because, last=r["last"], chg_pct=r["chg"]))
        out.sort(key=lambda s: s["score"], reverse=True)
        return out

    profiles = {name: build_list(W) for name, W in PROFILES.items()}
    out = {"generated": str(pd.Timestamp.today().date()), "universe": uni["universe"],
           "disclaimer": uni["disclaimer"],
           "universe_size": len(tickers), "scored": len(df),
           "calibration": cal_meta,          # null until backtest.py has been run
           "stocks": profiles["balanced"],   # backward-compatible default
           "profiles": profiles,
           "profile_weights": PROFILES}       # single source of truth for "How we score"
    json.dump(out, open(FILE, "w", encoding="utf-8"), ensure_ascii=False)

    dropped = [t for t in tickers if t not in df.index]
    if dropped:
        print(f"skipped {len(dropped)} ticker(s) this run (too little history or no data): "
              + ", ".join(t.replace('.BK', '') for t in dropped))
        print("  they stay in universe.json and will be retried tomorrow.")
    print(f"wrote {len(df)} stocks x 3 profiles -> today.json")
    for name, lst in profiles.items():
        n = {v: sum(s["verdict"] == v for s in lst) for v in ("BUY", "WAIT", "AVOID")}
        top = ", ".join(s["ticker"].replace(".BK", "") for s in lst[:5])
        print(f"  {name:<13} BUY {n['BUY']:>2}/WAIT {n['WAIT']:>2}/AVOID {n['AVOID']:>2}  | top5: {top}")


if __name__ == "__main__":
    main()
