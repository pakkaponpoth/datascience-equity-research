"""BLIND TEST - one shot, pre-registered, on a period we have never inspected.

    python blind_test.py

WHY THIS EXISTS
---------------
By 31 Aug 2026 we had run five backtest scripts x three profiles over roughly
2016-2026 - about fifteen looks at the same decade - and seen the `aggressive`
weight set beat buy-and-hold with a 96% luck bar. That number cannot be trusted
as evidence: we chose which result to be interested in *after* seeing it. Any
further claim about that decade is data-snooped.

The fix is to test the same frozen rule on data whose results we have never
looked at, decide in advance what would count as success, and run it once.


PRE-REGISTRATION  (written before the first execution, 2026-08-31)
------------------------------------------------------------------
H1  The frozen `aggressive` weight set produces higher 12-month forward returns
    than an equal-weight hold of the same universe.

SEALED PERIOD      score months 1999-01 .. 2014-12  (holds complete by 2015-12)
                   Never examined in isolation. Only ever seen folded inside a
                   single "full window" cumulative number.
DEVELOPMENT PERIOD score months 2016-01 .. present. Examined ~15 times. Reported
                   here only as the contaminated comparison, never as evidence.
                   A one-year gap (2015) keeps the two windows from overlapping.

FROZEN INPUTS      Weights copied verbatim from run_today.py. Not re-tuned, not
                   re-chosen, not reordered. Universe = universe.json. Top 20%,
                   12-month hold, equal weight - identical to backtest_profiles.py.

DECISION RULE, committed in advance:
    REPLICATES         beats buy-and-hold AND luck bar >= 90%
    WEAK               beats buy-and-hold but luck bar < 90%
    DOES NOT REPLICATE does not beat buy-and-hold

    Because three profiles are tested, a 90% luck bar on the best of three is
    roughly a 73% chance under the null (0.9^3). The Sidak-corrected bar for a
    genuine 90% claim across three profiles is 96.6%, and it is reported too.

RUN ONCE. If anything above is edited and the script re-run, the result stops
being blind and must be reported as exploratory. The first run's output is
preserved in reports/blind_test.md.


KNOWN BIASES THIS TEST DOES *NOT* FIX
-------------------------------------
Survivorship. The universe is today's SET100 members, so the sealed period is
scored using companies we already know survived to 2026. This inflates every
arm - picks, benchmark and random books alike - so the *comparison* is still
informative while the absolute levels are not. Stock coverage per period is
printed so the size of the problem is visible.
"""
import numpy as np
import pandas as pd
import yfinance as yf
from reportlib import capture, load_universe

capture("blind_test", "Blind test - frozen rule on a never-inspected period",
        {"design": "pre-registered, one shot",
         "sealed": "score 1999-01 to 2014-12, holds complete by 2015-12",
         "development": "score 2016-01 to present (contaminated, shown for contrast)",
         "frozen": "weights verbatim from run_today.py; top 20%; 12-month hold",
         "decision rule": "REPLICATES = beats B&H and luck bar >= 90%"})

meta, uni_src = load_universe()
tickers = list(meta)
FACT = ["momentum", "growth", "value", "quality", "health"]
PROFILES = {                                   # FROZEN - identical to run_today.py
    "conservative": {"quality": .40, "health": .30, "value": .20, "momentum": .05, "growth": .05},
    "balanced":     {"quality": .28, "value": .24, "momentum": .20, "health": .16, "growth": .12},
    "aggressive":   {"momentum": .40, "growth": .30, "value": .15, "quality": .10, "health": .05},
}
H, K = 12, 300
np.random.seed(7)

print(f"universe: {len(tickers)} tickers from {uni_src}")
print("fetching MAX monthly history...")
px = yf.download(tickers, period="max", auto_adjust=True, progress=False)["Close"].dropna(how="all")
mpx = px.resample("ME").last()
rets = mpx.pct_change(fill_method=None)
print(f"history: {mpx.index[0].date()} -> {mpx.index[-1].date()}  ({len(mpx)} months)")


def adj_month(i):
    """Sector-neutral factor z-scores using data up to month i only."""
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


def run_window(first, last, label):
    """Score every month in [first, last], hold H months, no look-ahead."""
    res = {p: {"ret": [], "rand": [[] for _ in range(K)]} for p in PROFILES}
    bench, dates, coverage = [], [], []
    for i in range(12, len(mpx) - H):
        d = mpx.index[i]
        if not (first <= d <= last):
            continue
        adj = adj_month(i)
        if adj is None:
            continue
        hold = rets.iloc[i + 1:i + 1 + H]           # the H months AFTER i
        idx = adj.index
        coverage.append(len(idx))
        dates.append(d)
        bench.append((1 + hold[idx].mean(axis=1)).prod() - 1)
        pool = list(idx)
        n = 0
        for p, W in PROFILES.items():
            sc = sum(W[f] * adj[f] for f in FACT).rank(pct=True)
            picks = sc[sc >= sc.quantile(0.80)].index
            n = len(picks)
            res[p]["ret"].append((1 + hold[picks].mean(axis=1)).prod() - 1)
        for k in range(K):
            rp = np.random.choice(pool, min(n, len(pool)), replace=False)
            rr = (1 + hold[rp].mean(axis=1)).prod() - 1
            for p in PROFILES:
                res[p]["rand"][k].append(rr)

    if not bench:
        print(f"\n{label}: no usable months - skipped")
        return None

    b = float(np.mean(bench))
    print(f"\n=== {label} ===")
    print(f"start-points: {len(bench)}   ({dates[0].date()} -> {dates[-1].date()})")
    print(f"stocks with usable history: {min(coverage)}-{max(coverage)} "
          f"(median {int(np.median(coverage))} of {len(tickers)})")
    print(f"buy & hold (equal weight, {H}-month hold): {b*100:+.1f}% avg\n")
    print(f"{'profile':<14}{'avg 12mo':>10}{'vs B&H':>9}{'luck bar':>10}{'verdict':>22}")
    out = {}
    for p in PROFILES:
        r = float(np.mean(res[p]["ret"]))
        rand_avg = sorted(float(np.mean(x)) for x in res[p]["rand"])
        luck = 100 * sum(1 for x in rand_avg if x < r) / K
        if r <= b:
            v = "DOES NOT REPLICATE"
        elif luck >= 90:
            v = "REPLICATES"
        else:
            v = "WEAK"
        print(f"{p:<14}{r*100:>9.1f}%{(r-b)*100:>+8.1f}{luck:>9.0f}%{v:>22}")
        out[p] = dict(ret=r, luck=luck, verdict=v, bench=b, per_start=res[p]["ret"])
    out["_dates"] = dates
    out["_bench_per_start"] = bench
    return out


def blocks(result, dates, label, years=3):
    """Non-overlapping blocks - one aggregate number is easy to be lucky in."""
    if not result:
        return
    print(f"\n--- {label}: non-overlapping {years}-year blocks (robustness) ---")
    print(f"{'block':<16}{'aggressive':>12}{'B&H':>9}{'beat?':>8}")
    idx = pd.DatetimeIndex(dates)
    agg = np.array(result["aggressive"]["per_start"])
    ben = np.array(result["_bench_per_start"])
    wins = total = 0
    y0, y1 = idx[0].year, idx[-1].year
    for start in range(y0, y1 + 1, years):
        m = (idx.year >= start) & (idx.year < start + years)
        if m.sum() < 6:
            continue
        a = float(np.mean(agg[m]))
        b = float(np.mean(ben[m]))
        total += 1
        wins += a > b
        print(f"{start}-{start+years-1:<11}{a*100:>11.1f}%{b*100:>8.1f}%{'yes' if a > b else 'no':>8}")
    if total:
        print(f"beat buy-and-hold in {wins}/{total} blocks "
              f"({100*wins/total:.0f}%) - coin-flip expectation is 50%")


if __name__ == "__main__":
    SEALED = (pd.Timestamp("1999-01-01"), pd.Timestamp("2014-12-31"))
    DEV = (pd.Timestamp("2016-01-01"), mpx.index[-1])

    print("\n" + "=" * 66)
    print("SEALED PERIOD - the blind test. This is the evidence.")
    print("=" * 66)
    sealed = run_window(*SEALED, "SEALED 1999-2014 (never inspected)")
    if sealed:
        blocks(sealed, sealed["_dates"], "SEALED")

    print("\n" + "=" * 66)
    print("DEVELOPMENT PERIOD - contaminated. Shown for contrast, NOT evidence.")
    print("=" * 66)
    run_window(*DEV, "DEVELOPMENT 2016-now (already examined ~15 times)")

    print("\n" + "=" * 66)
    print("HOW TO READ THIS")
    print("=" * 66)
    print("The sealed result is the only one that carries evidential weight.")
    print("If sealed and development disagree, the development result was the")
    print("story we told ourselves after seeing the data - not a finding.")
    print("Sidak-corrected bar for a genuine 90% claim across 3 profiles: 96.6%.")
    print("Survivorship bias is NOT corrected: the universe is today's SET100,")
    print("so absolute levels are inflated in every arm. Compare, do not quote.")
