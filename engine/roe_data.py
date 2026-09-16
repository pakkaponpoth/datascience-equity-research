"""Point-in-time ROE, read from roe_history.csv. The one place that file is parsed.

WHY THIS FILE EXISTS
--------------------
ROE is the only factor that does not come from the price series, so it is the
only one that can leak the future. A fiscal year's ROE must not be visible to a
backtest standing in January of the following year, because nobody could read
the statement yet.

  ROE = net profit attributable to owners of the parent
        / average shareholders' equity (this year end + last year end) / 2

usable_from is 1 April of the year AFTER the fiscal year: Thai listed companies
must file audited annual statements within three months of their year end. The
filings themselves carry no submission date, so that deadline stands in for it.
Every consumer must go through roe_asof() rather than reading the CSV, for the
same reason factors.py exists - a rule copied into seven scripts is a rule that
will drift in six of them.

WHERE THE DATA COMES FROM
-------------------------
1,591 stock-years for 94 of the 95 stocks, 2001-2026, read out of the annual
statements in SEC Thailand's disclosure archive (the spreadsheet attached to
each filing). 93% of the overlapping years agree with Yahoo within 2 points;
where they disagree the archive is the one to trust, because it is the original
filing rather than a figure restated after a later merger.

Known gaps: BANPU (its filings are not reachable through the SEC search), and
GULF and TIDLOR stop at fiscal 2024. A missing ROE is not an error - see
run_today.py for how a stock with no ROE is scored.

REFRESHING IT
-------------
Annual data, so once a year, after April. The builder lives in the research
sandbox (research/roe_pilot.py); this repo carries only its output.
"""
import csv
import datetime as dt
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(HERE, "roe_history.csv")

_HISTORY = None


def _as_date(when):
    """Accept a date, a datetime, a pandas Timestamp, or 'YYYY-MM-DD'."""
    if isinstance(when, str):
        return dt.date.fromisoformat(when[:10])
    if isinstance(when, dt.date) and not isinstance(when, dt.datetime):
        return when
    return when.date()          # datetime and pandas Timestamp both have .date()


def _bare(ticker):
    """ADVANC.BK -> ADVANC. The CSV keys on the SET symbol, not the Yahoo one."""
    return ticker.split(".")[0].upper()


def history():
    """{TICKER: [(usable_from, roe), ...]} sorted by date. Parsed once."""
    global _HISTORY
    if _HISTORY is None:
        out = {}
        with open(CSV_FILE, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                out.setdefault(_bare(row["ticker"]), []).append(
                    (dt.date.fromisoformat(row["usable_from"]), float(row["roe"])))
        for t in out:
            out[t].sort()
        _HISTORY = out
    return _HISTORY


def roe_asof(ticker, when):
    """The most recent ROE a reader could have seen on `when`, else None."""
    when = _as_date(when)
    latest = None
    for usable_from, roe in history().get(_bare(ticker), ()):
        if usable_from <= when:
            latest = roe
        else:
            break
    return latest


def neutral_fill(values):
    """Missing ROE -> the median of the stocks we do have. Deliberately "no opinion".

    The alternative - dropping a stock that has no filed ROE - would quietly
    shrink the universe, most of all in the early years where coverage is
    thinnest, and would change what the backtest is even measuring. Scoring it
    at the median neither rewards nor punishes it on the one factor we cannot
    see for it, and keeps the live list and the backtests doing the same thing.
    """
    known = sorted(v for v in values if v is not None and v == v)   # v == v drops NaN
    if not known:
        return [0.0] * len(values)
    mid = len(known) // 2
    median = known[mid] if len(known) % 2 else (known[mid - 1] + known[mid]) / 2
    return [median if (v is None or v != v) else v for v in values]


def coverage(tickers, when):
    """(n_with_roe, n_total) - so a caller can report the gap instead of hiding it."""
    have = sum(1 for t in tickers if roe_asof(t, when) is not None)
    return have, len(tickers)
