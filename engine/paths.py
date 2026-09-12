"""Where the data and the reports live - the one place that knows.

This code exists in two layouts:

    team repo   engine/<scripts>    engine/universe.json     reports/
    atlas       research/<scripts>  setscout/universe.json   setscout/reports/

The data sits BESIDE the scripts in one layout and ONE LEVEL UP in the other,
while reports/ is one level up in both. Every script used to hard-code "one
level up", which is right for atlas and silently wrong for the team repo: the
backtests could not find universe.json there, and backtest.py would have
written a re-measured calibration.json to a folder run_today.py never reads.

Import from here instead of rebuilding the path in each script. Importing this
module has no side effects - it only computes three folder names.
"""
import os

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(SCRIPTS)

# reports/ is one level above the scripts in both layouts
REPORTS = os.path.join(PARENT, "reports")


def _data_dir():
    """The folder holding universe.json (or, in old checkouts, today.json)."""
    for name in ("universe.json", "today.json"):
        for folder in (SCRIPTS, PARENT):
            if os.path.exists(os.path.join(folder, name)):
                return folder
    return PARENT   # nothing found: callers raise their own clear error


# universe.json, today.json, calibration.json and the price caches live here
DATA = _data_dir()
