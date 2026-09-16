"""SETScout backtest — the honesty check.

    python backtest.py

Point-in-time monthly backtest of the SAME scoring pipeline as run_today.py:
each month we score every stock using ONLY past data (no look-ahead), buy the
top 20%, hold one month, repeat. Then we answer three honest questions:
  1) Does it beat buy-and-hold (equal-weight the universe)?
  2) The LUCK BAR — is it better than picking the same number of stocks at random?
  3) Calibrate p_win — historically, how often did each score-bucket actually go up?
The up-rate in (3) is a FINDING, not a feature: it came out flat at ~47% across
every score band (p = 0.53), so the app publishes no per-stock hit rate at all.
The table below is the evidence, and it lands in reports/. Nothing reads it at
runtime, so nothing can quietly go stale.
"""
import json, math, os
import numpy as np, pandas as pd, yfinance as yf
from reportlib import capture, load_universe
from factors import FACTORS as FACT, PROFILES   # single source of truth
from roe_data import roe_asof, neutral_fill              # point-in-time ROE, see roe_data.py
W = PROFILES["balanced"]

capture("backtest", "Monthly rotation backtest - the honesty check",
        {"rebalance": "monthly, buy top 20%", "history": "~8y monthly", "luck bar": "300 random portfolios", "outputs": "the up-rate table below - a finding, not a runtime input"})

# universe.json / price-cache folder - see paths.py
from paths import DATA
meta, _uni_src = load_universe()
tickers = list(meta)
print(f"universe: {len(tickers)} tickers from {_uni_src}")
K = 300                      # random portfolios for the luck bar
np.random.seed(7)

print(f"{len(tickers)} tickers - fetching ~8y monthly prices...")
px = yf.download(tickers, period="8y", auto_adjust=True, progress=False)["Close"].dropna(how="all")
mpx = px.resample("ME").last()
# A month that has not ended is not a month. Without this, running on the 13th
# scores August against a 13-day "September" return, so every figure below
# would depend on the day of the month the script happened to be run.
if mpx.index[-1] > pd.Timestamp.today().normalize():
    mpx = mpx.iloc[:-1]
rets = mpx.pct_change(fill_method=None)


def score_month(i):
    """percentile score per stock at month i, using data up to i only."""
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
        rows[t] = dict(momentum=s.iloc[-1] / s.iloc[-7] - 1,
                       roe=roe_asof(t, hp.index[-1]),
                       quality=-r12.std() * np.sqrt(12),
                       health=(eq / eq.cummax() - 1).min(), sector=meta[t])
    if len(rows) < 10:
        return None
    df = pd.DataFrame(rows).T
    df["roe"] = neutral_fill(list(df["roe"]))   # see roe_data.py
    for f in FACT:
        c = df[f].astype(float); sd = c.std(ddof=0)
        df[f] = ((c - c.mean()) / (sd if sd > 0 else 1.0)).clip(-3, 3)
    big = set(df["sector"].value_counts().loc[lambda c: c >= 3].index)
    inb = df["sector"].isin(big)
    for f in FACT:
        df[f] = df[f] - df.groupby("sector")[f].transform("mean").where(inb, 0.0)
    return (sum(W[f] * df[f] for f in FACT)).rank(pct=True)


strat, bench, rand, calib = [], [], [[] for _ in range(K)], []
months = mpx.index
for i in range(12, len(months) - 1):
    sc = score_month(i)
    if sc is None:
        continue
    fwd = rets.iloc[i + 1]                       # realized NEXT month (no look-ahead)
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

cum = lambda xs: float(np.prod([1 + x for x in xs]) - 1)
n_mo = len(strat)
s_tot, b_tot = cum(strat), cum(bench)
rand_tot = sorted(cum(r) for r in rand)
luck_pct = 100 * sum(1 for r in rand_tot if r < s_tot) / K       # % of random books we beat
s_cagr = (1 + s_tot) ** (12 / n_mo) - 1
b_cagr = (1 + b_tot) ** (12 / n_mo) - 1
win_rate = 100 * sum(1 for x in strat if x > 0) / n_mo
sharpe = np.mean(strat) / (np.std(strat) or 1) * np.sqrt(12)

print("\n=== SETScout backtest ===")
print(f"months tested: {n_mo}  ({months[12].date()} -> {months[-1].date()})")
print(f"strategy total: {s_tot*100:+.1f}%   (CAGR {s_cagr*100:+.1f}%)")
print(f"buy & hold    : {b_tot*100:+.1f}%   (CAGR {b_cagr*100:+.1f}%)")
print(f"vs B&H        : {(s_tot-b_tot)*100:+.1f} pts   -> {'BEATS' if s_tot>b_tot else 'trails'} buy & hold")
print(f"monthly win-rate: {win_rate:.0f}%   Sharpe(annual): {sharpe:.2f}")
print(f"LUCK BAR: beat {luck_pct:.0f}% of {K} random portfolios "
      f"(random median {np.median(rand_tot)*100:+.1f}%)  -> "
      f"{'edge looks real' if luck_pct>=90 else 'within luck - not proven' if luck_pct<75 else 'borderline'}")

# ---- does a higher score mean a higher chance of rising? ----
cal = pd.DataFrame(calib, columns=["score", "win"])
cal["bucket"] = (cal["score"] * 10).clip(0, 9).astype(int)
tbl = cal.groupby("bucket")["win"].agg(["mean", "count"])
print("\n=== up-rate by score band (a finding - nothing reads this at runtime) ===")
for b, row in tbl.iterrows():
    print(f"  score {b*10:>2}-{b*10+10:<3}: won {row['mean']*100:4.1f}%   (n={int(row['count'])})")
rates = [float(r['mean']) for _, r in tbl.iterrows()]
print(f"\n  flat at {sum(rates)/len(rates)*100:.1f}% across {len(rates)} bands, "
      f"spread {(max(rates)-min(rates))*100:.1f}pp over {n_mo} months, "
      f"n = {int(tbl['count'].sum())} stock-months")

# Ten noisy percentages cannot be judged by eye, and REPORT 5.1 quotes these two
# statistics, so they are computed here. A statistic typed into a document by
# hand is a statistic that drifts the next time the engine changes.
#   Cochran-Armitage - is there a TREND from the low deciles to the high ones?
#   chi-square       - are the ten different at all, in any order?
n_i = tbl["count"].to_numpy(dtype=float)
p_i = tbl["mean"].to_numpy(dtype=float)
x_i = np.arange(10.0)                        # decile index, equally spaced
N = float(n_i.sum())
p_bar = float(cal["win"].mean())
x_bar = float((n_i * x_i).sum() / N)
den = math.sqrt(p_bar * (1 - p_bar) * float((n_i * (x_i - x_bar) ** 2).sum()))
z = float((n_i * (x_i - x_bar) * (p_i - p_bar)).sum()) / den if den else float("nan")
p_two = math.erfc(abs(z) / math.sqrt(2))     # two-sided normal p-value, exact
chi2 = float((n_i * (p_i - p_bar) ** 2 / (p_bar * (1 - p_bar))).sum())
CRIT_95_DF9 = 16.919                         # chi-square 5% critical value, df = 9
print(f"  trend from low scores to high (Cochran-Armitage): z = {z:+.2f}, p = {p_two:.2f}"
      f"  -> {'a trend' if p_two < 0.05 else 'NO trend'}")
print(f"  any difference at all (chi-square): {chi2:.1f} on df 9, "
      f"{'above' if chi2 > CRIT_95_DF9 else 'below'} the 5% critical value {CRIT_95_DF9}")
print("  -> the score does not predict direction. No p_win is published.")
