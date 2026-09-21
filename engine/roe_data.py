"""Point-in-time ROE, read from roe_history.csv. The one place that file is parsed.

WHY THIS FILE EXISTS
--------------------
ROE is the only factor that does not come from the price series, so it is the
only one that can leak the future. A fiscal year's ROE must not be visible to a
backtest standing in January of the following year, because nobody could read
the statement yet.

  ROE = net profit attributable to owners of the parent
        / average shareholders' equity (this year end + last year end) / 2

A fiscal year becomes readable three months after it ENDS, because Thai listed
companies must file audited annual statements within three months of their year
end. The filings carry no submission date, so that deadline stands in for it.

Until 2026-09-20 this was hard-coded as "1 April of the next year", which is
only correct for a December year end. Four companies in the universe do not
close in December, and for them we were withholding a figure we already had for
up to a year - BTS and VGI were showing a stale ROE of the opposite sign. The
year ends below were read off the column dates of published balance sheets, not
typed from memory.

Every consumer must go through roe_asof() rather than reading the CSV, for the
same reason factors.py exists - a rule copied into seven scripts is a rule that
will drift in six of them.

WHERE THE DATA COMES FROM
-------------------------
1,586 stock-years across all 95 stocks, 2001-2026. 1,583 come from the annual
statements in SEC Thailand's disclosure archive (the spreadsheet attached to
each filing); the `source` column marks the three that do not.

BANPU has NO annual filing reachable through the SEC document search - a search
returns one Q2 document whatever is asked, and narrowing the date window returns
nothing at all, so this is an indexing gap rather than a parser failure. GULF and
TIDLOR have filings whose newest annual one would not parse. All three were
filled from SET's own factsheet API, which publishes "Shareholders' Equity" and
"Net Profit : Owners Of The Parent" as structured figures. The two sources were
checked against each other first: PTT's FY2025 is 7.92% from SET and 7.92% from
the SEC filings. 93% of the overlapping years agree with Yahoo within 2 points;
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

# Month each company closes its books. Anything not listed closes in December.
# Derived 2026-09-20 from the fiscal period-end dates on published balance
# sheets for all 95 stocks; 91 close in December and these four do not.
FY_END_MONTH = {
    "AEONTS": 2,     # closes end of February
    "AOT": 9,        # closes 30 September
    "BTS": 3,        # closes 31 March
    "VGI": 3,        # closes 31 March
}

_HISTORY = None


def usable_from(ticker, fiscal_year):
    """The date a fiscal year's ROE could first have been read.

    Three months after the year ends, rounded up to the first of the month:

        December year end   FY2024 ends 31 Dec 2024  ->  1 Apr 2025
        March year end      FY2026 ends 31 Mar 2026  ->  1 Jul 2026
        September year end  FY2025 ends 30 Sep 2025  ->  1 Jan 2026

    The December case reproduces the old hard-coded rule exactly, so nothing
    moves for the 91 companies that close in December.
    """
    end_month = FY_END_MONTH.get(_bare(ticker), 12)
    total = end_month + 4                       # +3 months, then round up to the 1st
    return dt.date(fiscal_year + (total - 1) // 12, (total - 1) % 12 + 1, 1)


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


# ---------------------------------------------------------------- quality gate
#
# An audit on 2026-09-20 found rows that are wrong in a way the extraction
# cannot notice: a net profit read at the wrong scale produces an ROE of 0.02%
# sitting between neighbours of 12%. It is not impossible - a company can have a
# break-even year - so neither test alone is safe. Both together are: a value
# near zero AND fifty times smaller than the same company's own surrounding
# years is a parse failure, not a business event.
#
# A flagged year is treated exactly like BANPU, which has no filings at all:
# roe_asof returns None, the engine scores it at the universe median, and the
# card shows a dash. Publishing a dash costs a little information. Publishing a
# wrong number next to a company's name costs credibility, which is the thing
# this project is actually built on.

IMPOSSIBLE = 1.0        # |ROE| above 100% cannot be a real annual figure
NEAR_ZERO = 0.005       # 0.5%
OFF_BY = 50             # times smaller than its own neighbours


def _suspect(values, i):
    """True when a value is near zero and dwarfed by its neighbours, or repeated.

    A real ROE does not land on the same figure two years running to six decimal
    places - MEGA carried 14.2436% for 2014, 2015, 2016 AND 2017, which is the
    parser re-reading one column, not a business that earned the same return
    four years in a row.
    """
    roe = values[i][1]
    if abs(roe) > IMPOSSIBLE:
        return True
    if i and values[i - 1][1] == roe and roe != 0:
        return True
    if abs(roe) >= NEAR_ZERO:
        return False
    neigh = [abs(row[1]) for j, row in enumerate(values)
             if j != i and abs(i - j) <= 2 and row[1]]
    if len(neigh) < 2:
        return False                       # too little context to judge
    median = sorted(neigh)[len(neigh) // 2]
    return median > 0 and (roe == 0 or median / abs(roe) > OFF_BY)


def flagged():
    """[(ticker, fiscal_year, roe), ...] - every value the gate is withholding."""
    out = []
    for t, vals in _raw_history().items():
        for i, row in enumerate(vals):
            if _suspect(vals, i):
                out.append((t, row[2], row[1]))
    return out


def history():
    """{TICKER: [(usable_from, roe), ...]} sorted by date. Parsed once."""
    global _HISTORY
    if _HISTORY is None:
        _HISTORY = {t: [(d, v) for i, (d, v, _fy) in enumerate(vals)
                        if not _suspect(vals, i)]
                    for t, vals in _raw_history().items()}
    return _HISTORY


_RAW = None


def _raw_history():
    """Everything in the file, gate not yet applied."""
    global _RAW
    if _RAW is None:
        out = {}
        with open(CSV_FILE, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                t = _bare(row["ticker"])
                # The date is COMPUTED here rather than read from the file, so the
                # rule lives in exactly one place and a stale column cannot
                # contradict it.
                fy = int(row["fiscal_year"])
                out.setdefault(t, []).append(
                    (usable_from(t, fy), float(row["roe"]), fy))
        for t in out:
            out[t].sort()
        _RAW = out
    return _RAW


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
