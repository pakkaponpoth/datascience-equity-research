"""Does the app's RISK-BASED SIZING help? - pre-registered, one shot.

    python backtest_sizing.py

WHY THIS EXISTS
---------------
Every other backtest here buys the top 20% in EQUAL amounts. But that is not
what the product tells users to do. SETScout shows a per-stock cap - "put at
most 30 baht of every 100 in this one" - derived from that stock's volatility
and scaled by the user's risk profile. That advice has never been tested.

So we have measured whether the RANKING works (it does not: up-rate flat at
~47%, 0% luck bar on the fair hold test) but never whether the SIZING works.
Sizing is the more defensible half of the product, because risk control can
work even when prediction does not - so it deserves its own honest test.


PRE-REGISTRATION  (written and committed before the first execution, 1 Sep 2026)
--------------------------------------------------------------------------------
H1  Weighting the top-20% basket by the app's own risk caps produces a LOWER
    maximum drawdown than weighting it equally.

    Note this is a hypothesis about RISK, not RETURN. Risk-based sizing does not
    claim to earn more; it claims you lose less in a bad stretch. Judging it on
    return would be testing the wrong thing, so return is reported but is not
    the criterion.

CONSTRUCTION RULE  (the decision that had to be made in advance)
    `max_weight` in today.json is a CAP, not a weight: the caps do not sum to
    100%, and the app never says how many stocks to buy. Turning caps into a
    portfolio therefore requires a rule, and several are defensible. We commit
    to ONE, chosen before seeing any result:

        weight_i = cap_i / sum(cap_j for j in picks)

    i.e. hold the same 19-ish names as the equal-weight test, but allocate in
    proportion to each stock's cap, normalised to fully invested.

    Why this one: the cap is inversely related to volatility, so proportional
    allocation is inverse-volatility weighting - a recognised technique, not
    something invented for this test. It keeps the book fully invested, so it
    is directly comparable to the equal-weight arm; a rule that parks the
    remainder in cash would change total exposure and confound the comparison.

    REJECTED alternatives, named so they cannot be quietly tried later:
      (b) equal weight capped at cap_i, excess redistributed
      (c) buy each at its full cap, remainder held as cash

CAP FORMULA  (monthly analogue of the live engine, stated explicitly)
    live engine, daily data:  risk = 1.645 * sd_daily * sqrt(21) * 100
    here, monthly data:       risk = 1.645 * sd_monthly * 100
    then, exactly as the app:  risk clamped to [6, 35]
                               cap = min(0.40, max(0.08, 0.42*(1-risk/32)))
                               cap *= profile multiplier (0.6 / 1.0 / 1.35)
                               cap clamped to [0.05, 0.60]

PRIMARY WINDOW  score months 2016-01 .. present.
    Unlike the ranking hypothesis, sizing has NEVER been examined on any period,
    so the data-snooping that forced blind_test.py onto a sealed window does not
    apply here. We choose the recent window because it has far better coverage
    (66-92 of 95 stocks have history, versus 37-62 pre-2015) and drawdown is a
    path statistic that needs reliable data. The sealed window is reported as a
    robustness check, not as the criterion.

DECISION RULE, committed in advance:
    SUPPORTED     max drawdown improves by >= 20% relative to equal weight,
                  AND return is no worse than 2.0 percentage points
    MIXED         drawdown improves by >= 20% but return cost exceeds 2.0 pts
    NOT SUPPORTED drawdown improvement < 20%

RUN ONCE. Editing anything above and re-running makes the result exploratory,
not pre-registered, and it must be reported as such.

KNOWN LIMITS
    Survivorship bias is uncorrected (same universe as every other test here).
    Both arms hold identical stocks, so the comparison is internal and the bias
    affects them equally - but absolute levels remain unquotable.
    Monthly rebalancing, as in the other backtests. No transaction costs: the
    two arms hold the same names and differ only in weights, so turnover is
    similar; a cost model would move both arms in the same direction.
"""
import numpy as np
import pandas as pd
import yfinance as yf
from reportlib import capture, load_universe

capture("backtest_sizing", "Does risk-based sizing help? - pre-registered, one shot",
        {"hypothesis": "risk-cap weighting lowers max drawdown vs equal weight",
         "construction": "weight = cap / sum(caps), fully invested",
         "primary window": "2016-01 to present (sizing never examined before)",
         "criterion": "drawdown improves >= 20% at <= 2.0 pts return cost",
         "note": "judged on RISK, not return"})

meta, uni_src = load_universe()
tickers = list(meta)
FACT = ["momentum", "growth", "value", "quality", "health"]
PROFILES = {                                    # FROZEN - identical to run_today.py
    "conservative": {"quality": .40, "health": .30, "value": .20, "momentum": .05, "growth": .05},
    "balanced":     {"quality": .28, "value": .24, "momentum": .20, "health": .16, "growth": .12},
    "aggressive":   {"momentum": .40, "growth": .30, "value": .15, "quality": .10, "health": .05},
}
SIZE_MULT = {"conservative": 0.6, "balanced": 1.0, "aggressive": 1.35}
H = 12

print(f"universe: {len(tickers)} tickers from {uni_src}")
print("fetching MAX monthly history...")
px = yf.download(tickers, period="max", auto_adjust=True, progress=False)["Close"].dropna(how="all")
mpx = px.resample("ME").last()
rets = mpx.pct_change(fill_method=None)
print(f"history: {mpx.index[0].date()} -> {mpx.index[-1].date()}  ({len(mpx)} months)")


def adj_month(i):
    """Sector-neutral factor z-scores AND each stock's monthly vol, using data <= i."""
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
                       health=(eq / eq.cummax() - 1).min(),
                       mvol=r12.std(), sector=meta[t])
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


def cap_for(mvol, mult):
    """The app's own cap formula, monthly analogue. See PRE-REGISTRATION."""
    risk = min(max(1.645 * float(mvol) * 100, 6.0), 35.0)
    cap = min(0.40, max(0.08, 0.42 * (1 - risk / 32.0)))
    return min(0.60, max(0.05, cap * mult))


def max_drawdown(monthly):
    """Worst peak-to-trough of the compounded path."""
    curve = (1 + pd.Series(monthly)).cumprod()
    return float((curve / curve.cummax() - 1).min())


def run(first, last, label, primary):
    eq_path, rw_path = {p: [] for p in PROFILES}, {p: [] for p in PROFILES}
    n_trials = 0
    for i in range(12, len(mpx) - 1):
        d = mpx.index[i]
        if not (first <= d <= last):
            continue
        adj = adj_month(i)
        if adj is None:
            continue
        nxt = rets.iloc[i + 1]                     # ONE month forward, no look-ahead
        n_trials += 1
        for p, W in PROFILES.items():
            sc = sum(W[f] * adj[f] for f in FACT).rank(pct=True)
            picks = sc[sc >= sc.quantile(0.80)].index
            r = nxt[picks].dropna()
            if r.empty:
                continue
            eq_path[p].append(float(r.mean()))     # equal weight
            caps = np.array([cap_for(adj.loc[t, "mvol"], SIZE_MULT[p]) for t in r.index])
            w = caps / caps.sum()                  # THE COMMITTED RULE
            rw_path[p].append(float((w * r.values).sum()))

    if not n_trials:
        print(f"\n{label}: no usable months")
        return
    print(f"\n{'=' * 70}")
    print(f"{label}   ({n_trials} monthly rebalances)" + ("   <-- PRIMARY" if primary else "   (robustness only)"))
    print(f"{'=' * 70}")
    print(f"{'profile':<14}{'arm':<14}{'maxDD':>9}{'ann vol':>9}{'ann ret':>9}"
          f"{'DD change':>11}{'ret cost':>10}")
    for p in PROFILES:
        e, r = eq_path[p], rw_path[p]
        if not e:
            continue
        stats = {}
        for name, path in (("equal weight", e), ("risk-weighted", r)):
            dd = max_drawdown(path)
            vol = float(np.std(path) * np.sqrt(12))
            ret = float((1 + pd.Series(path)).prod() ** (12 / len(path)) - 1)
            stats[name] = (dd, vol, ret)
            print(f"{p if name.startswith('equal') else '':<14}{name:<14}"
                  f"{dd * 100:>8.1f}%{vol * 100:>8.1f}%{ret * 100:>8.1f}%", end="")
            if name.startswith("equal"):
                print()
        dd_e, _, ret_e = stats["equal weight"]
        dd_r, _, ret_r = stats["risk-weighted"]
        improve = (abs(dd_e) - abs(dd_r)) / abs(dd_e) * 100 if dd_e else 0.0
        cost = (ret_e - ret_r) * 100
        print(f"{improve:>10.1f}%{cost:>+9.1f}")
        if primary:
            if improve >= 20 and cost <= 2.0:
                v = "SUPPORTED"
            elif improve >= 20:
                v = "MIXED - drawdown helped, return cost too high"
            else:
                v = "NOT SUPPORTED"
            print(f"{'':<28}verdict: {v}")


if __name__ == "__main__":
    run(pd.Timestamp("2016-01-01"), mpx.index[-1], "PRIMARY  2016-now", True)
    run(pd.Timestamp("1999-01-01"), pd.Timestamp("2014-12-31"), "ROBUSTNESS  1999-2014", False)
    print(f"\n{'=' * 70}")
    print("Pass mark was fixed before this ran: drawdown must improve >= 20%")
    print("at a return cost <= 2.0 points. Both arms hold the SAME stocks and")
    print("differ only in weights, so the comparison is internal - but the")
    print("universe is survivorship-biased, so do not quote absolute levels.")
