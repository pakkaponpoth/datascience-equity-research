"""SETScout engine — run once/day to refresh today.json with REAL data.

    python run_today.py

Reads the universe (tickers + Thai names + sectors) from universe.json, pulls
real prices from Yahoo Finance, scores every stock with a multi-factor
filter, and writes today.json. The website just reads that file.

universe.json is READ-ONLY here and today.json is WRITE-ONLY. That separation
matters: the engine used to read its own output, so any ticker that failed to
fetch once vanished from the universe forever (4 were lost that way). Now a
failed fetch is skipped for one run and retried the next day.

The four factors ask four different questions:
  momentum = 6-month return · roe = return on equity, from the annual filings ·
  quality = low volatility · health = small max-drawdown.
Two have been retired. "value" (cheapness vs the 200-day average) went on
2026-09-09 for correlating -0.93 with momentum - that factor negated, not a
separate one. "growth" (the 12-month return) went on 2026-09-16, replaced by
roe: it overlapped momentum at +0.66, and when the two were tested head to head
the 6-month return was the one worth keeping. See factors.py for the numbers,
including the honest caveat that roe did not improve returns.

NO p_win / HIT RATE. The app used to show a confidence figure per stock. The
measured up-rate turned out to be flat at ~47% across every score band
(p = 0.53 for any trend), so the figure said the same thing about every stock
while looking like a per-stock forecast. It is not emitted at all rather than
emitted and explained away. backtest.py still measures it - as a finding about
the engine, in reports/, which is where a null result belongs.

Scoring (less biased): each factor is winsorized + z-scored, then
SECTOR-NEUTRALIZED — a stock is judged against its SECTOR PEERS, not the whole
market — so one low-vol sector (e.g. banks) can no longer dominate the top.
Composite = weighted z-score; final score = its percentile across the market.

PERSONALIZATION: the same factors are combined with THREE weight sets, one per
risk profile, so the website's risk quiz can serve a matching list:
  conservative -> safety factors ·  balanced -> even ·  aggressive -> momentum.
Factor WEIGHTS are placeholders until the AHP expert survey sets them.
"""
import json, os, sys
import numpy as np, pandas as pd, yfinance as yf
from factors import FACTORS, PROFILES   # single source of truth - do not copy
from roe_data import roe_asof, coverage, neutral_fill  # point-in-time ROE - do not read the CSV directly

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "today.json")          # OUTPUT only - never read as input
UNIVERSE_FILE = os.path.join(HERE, "universe.json")   # INPUT - the canonical stock list


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


def main():
    uni, from_universe_file = load_universe()
    meta = {s["ticker"]: {"name": s["name"], "name_th": s["name_th"],
                          "sector": s["sector"]} for s in uni["stocks"]}
    tickers = list(meta)
    src = "universe.json" if from_universe_file else "today.json (fallback)"
    print(f"{len(tickers)} tickers from {src} - fetching ~2y prices...")
    today = pd.Timestamp.today().normalize()
    have_roe, n_roe = coverage(tickers, today)
    print(f"ROE: {have_roe}/{n_roe} tickers have a filed ROE usable today")
    px = yf.download(tickers, period="2y", auto_adjust=True, progress=False)["Close"]
    px = px.dropna(how="all")

    rows = {}
    for t in tickers:
        s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
        if len(s) < 130:
            continue
        rows[t] = dict(
            momentum=s.iloc[-1] / s.iloc[-126] - 1,
            roe=roe_asof(t, today),
            quality=-s.pct_change().tail(252).std() * np.sqrt(252),
            health=(s.tail(252) / s.tail(252).cummax() - 1).min(),
            last=round(float(s.iloc[-1]), 2),
            chg=round(float(s.pct_change().iloc[-1] * 100), 1),
            dvol=s.pct_change().tail(252).std())
    df = pd.DataFrame(rows).T
    df["sector"] = [meta[t]["sector"] for t in df.index]

    # A stock with no filed ROE (BANPU, and any company whose latest statement
    # could not be read) is scored at the universe median instead of being
    # dropped from the list. That is a deliberate "no opinion": it neither
    # rewards nor punishes the stock on a factor we have no data for. The flag
    # travels with the stock so the gap is visible rather than silent.
    df["roe"] = pd.to_numeric(df["roe"], errors="coerce")
    no_roe = df["roe"].isna()
    df["roe"] = neutral_fill(list(df["roe"]))

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
                risk_month_pct=risk, max_weight=mw,
                # null, not the median stand-in, when the filing could not be read:
                # the card shows a dash rather than a number the company never reported
                roe_pct=None if bool(no_roe[t]) else round(float(r["roe"]) * 100, 1),
                because=because, last=r["last"], chg_pct=r["chg"]))
        out.sort(key=lambda s: s["score"], reverse=True)
        return out

    profiles = {name: build_list(W) for name, W in PROFILES.items()}
    out = {"generated": str(pd.Timestamp.today().date()), "universe": uni["universe"],
           "disclaimer": uni["disclaimer"],
           "universe_size": len(tickers), "scored": len(df),
           "roe_coverage": {"with_roe": int((~no_roe).sum()), "scored": int(len(df)),
                            "note": "Stocks with no filed ROE are scored at the "
                                    "universe median on that factor, not dropped."},
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
