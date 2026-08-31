"""Make every backtest leave a reproducible artifact behind.

Until now the backtests printed their results and that was the only place the
numbers existed - console scrollback. Anything the report cites has to be
reproducible and citable, so each script now mirrors its full output into
`reports/<slug>.md` with a run stamp and its parameters.

One line per script, right after the imports:

    from reportlib import capture
    capture("backtest_hold", "Hold test - buy the picks and hold H months",
            {"universe": "SET100", "holds": "6 and 12 months"})

Everything after that is captured automatically (stdout *and* stderr, so a
failed run is self-documenting) and written at exit. No changes to the existing
print() calls, and the console behaves exactly as before.
"""
import atexit
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.join(os.path.dirname(HERE), "reports")


class _Tee:
    """Write through to the real stream, keeping a copy."""

    def __init__(self, stream):
        self.stream = stream
        self.buf = []

    def write(self, s):
        self.stream.write(s)
        self.buf.append(s)
        return len(s)

    def flush(self):
        self.stream.flush()

    def isatty(self):
        return getattr(self.stream, "isatty", lambda: False)()


def capture(slug, title, params=None):
    """Start recording this script's output into reports/<slug>.md."""
    out_tee, err_tee = _Tee(sys.stdout), _Tee(sys.stderr)
    sys.stdout, sys.stderr = out_tee, err_tee
    started = datetime.datetime.now()

    def _save():
        sys.stdout, sys.stderr = out_tee.stream, err_tee.stream
        body = "".join(out_tee.buf).rstrip()
        errs = "".join(err_tee.buf).strip()
        took = (datetime.datetime.now() - started).total_seconds()

        doc = [
            f"# {title}",
            "",
            f"*Run {started:%Y-%m-%d %H:%M} &middot; took {took:.0f}s &middot; "
            f"reproduce with `python {slug}.py`*",
            "",
        ]
        if params:
            doc += ["## Parameters", ""]
            doc += [f"- **{k}**: {v}" for k, v in params.items()]
            doc += [""]
        doc += ["## Output", "", "```", body, "```", ""]
        if errs:
            doc += ["## Warnings / errors on stderr", "",
                    "> Present because the run logged to stderr - usually "
                    "yfinance reporting a delisted ticker. Check before citing.",
                    "", "```", errs[:4000], "```", ""]

        os.makedirs(REPORTS, exist_ok=True)
        path = os.path.join(REPORTS, f"{slug}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(doc))
        print(f"\n-> saved reports/{slug}.md")

    atexit.register(_save)


def load_universe():
    """Canonical ticker list, matching run_today.py.

    The backtests used to read their universe from today.json, which the engine
    overwrites - so a test could silently run on a different set of stocks than
    the one being scored. universe.json is the single source of truth.
    """
    import json
    for name in ("universe.json", "today.json"):
        try:
            u = json.load(open(os.path.join(HERE, name), encoding="utf-8"))
            return {s["ticker"]: s["sector"] for s in u["stocks"]}, name
        except OSError:
            continue
    raise SystemExit("no universe.json or today.json found")
