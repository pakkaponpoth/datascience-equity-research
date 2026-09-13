"""Facts lint - fail when a doc or page contradicts the code.

    python tools/facts_lint.py             # check the repo
    python tools/facts_lint.py --selftest  # prove every rule catches and allows correctly

WHY THIS EXISTS
---------------
This repo keeps logging one failure mode (docs/CONTINUE.md): a fact recorded in
one place and never updated where it is repeated. Five instances by 13 Sep 2026,
four of them in prose - "~92 stocks", "five factors", p_win "a placeholder
formula", ranks marked *re-derive*, and "measured over 84 months" typed into a
page. Each was found by a person, days late. This finds them on the pull request.

HOW IT WORKS
------------
The truth comes from the code, never from this file:

    factor count      len(FACTORS)                 engine/factors.py
    stock count       len(stocks)                  engine/universe.json
    months measured   months                       engine/calibration.json

Then every current-tense doc and page is scanned for statements that disagree.

RULES
-----
  factor-count   "N factors" / "N ปัจจัย" where N >= 3 and N != len(FACTORS)
  stock-count    "N stocks|tickers|SET|หุ้น" where 50 <= N <= 250 and N != stock count
  months-page    a month count (24-240) typed into app/*.html - pages must read it
                 from the data (DATA.calibration.months), or it goes stale on the
                 next re-measurement
  months-doc     a month count on a doc line about calibration / p_win / up-rate /
                 deciles that differs from calibration.json
  pairwise-count "N pairwise" comparisons where N != F x (F-1) / 2 - the AHP survey
                 size follows the factor count (its first real catch: REPORT 9 still
                 said "ten", the five-factor number)
  stale-claim    phrases that were true once and are known false now

HISTORY IS ALLOWED
------------------
A line that describes the past is not a contradiction. A finding is skipped when
its line contains a history marker - "original", "old", "used to", "was", "had",
"said", "showed", "before", "removed", "earlier", "draft", "เดิม", "เคย", or an
arrow "→".
Anything else deliberate can be silenced on that line with:  facts-lint: ignore

NOT SCANNED
-----------
docs/CHANGELOG.md (history by design), docs/HANDOFF.md (the original design
brief - its own banner says it is superseded), reports/ (dated evidence - never
edit), proposals/ (the original plan, kept as written).

Standard library only, so CI needs no installs.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"

SCAN = ["README.md", "START-HERE.md", "docs/*.md", "app/*.html",
        "0-if-you-have-no-idea/*.md", "research/*.md"]
SKIP = {"docs/CHANGELOG.md", "docs/HANDOFF.md"}

WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10}

HISTORY = re.compile(
    r"\b(original|originally|old|older|used to|previously|before|was|were|had|"
    r"said|showed|removed|earlier|draft|until)\b|เดิม|เคย|→", re.I)
IGNORE = "facts-lint: ignore"

FACTOR_RE = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b"
    r"\s+(?:[A-Za-z\"'*_-]+\s+){0,2}factors?\b", re.I)
FACTOR_TH = re.compile(r"(\d+)\s*ปัจจัย")
STOCK_RE = re.compile(
    r"~?\b(\d{2,3})\b\s+(?:[A-Za-z0-9-]+\s+){0,3}?(?:stocks|tickers)\b"
    r"|~?\b(\d{2,3})\s+SET\b"
    r"|(\d{2,3})\s*หุ้น", re.I)
MONTHS_RE = re.compile(r"\b(\d{2,3})\s*(?:complete\s+)?(?:months?|เดือน)", re.I)
CALIB_CONTEXT = re.compile(r"calibration|p_win|up-rate|decile|trust label", re.I)
PAIR_RE = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b"
    r"\s+(?:[A-Za-z-]+\s+){0,1}?pairwise\b", re.I)

STALE = [
    (re.compile(r"placeholder formula", re.I),
     "p_win reads the measured calibration.json; it is not a placeholder"),
    (re.compile(r"top decile (?:is |was )?the lowest", re.I),
     "re-measured on four factors, the top decile is not the lowest (noise, p = 0.53)"),
    (re.compile(r"wire calibration", re.I),
     "calibration is wired into run_today.py"),
    (re.compile(r"\*re-derive\*", re.I),
     "REPORT 3.4 ranks have been re-derived"),
    (re.compile(r"barely distinguishable", re.I),
     "balanced is no longer a copy of conservative (REPORT 7)"),
    (re.compile(r"genuinely in the middle", re.I),
     "balanced still leans cautious - do not overclaim"),
]


def load_truth():
    sys.path.insert(0, str(ENGINE))
    from factors import FACTORS  # noqa: E402 - factors.py has no imports of its own
    uni = json.loads((ENGINE / "universe.json").read_text(encoding="utf-8"))
    cal = json.loads((ENGINE / "calibration.json").read_text(encoding="utf-8"))
    return {"factors": len(FACTORS), "stocks": len(uni["stocks"]),
            "months": int(cal["months"])}


def as_int(token):
    token = token.lower()
    return WORDS.get(token, int(token) if token.isdigit() else None)


def check_line(line, truth, is_page):
    """Return a list of (rule, message) for one line of text."""
    if IGNORE in line:
        return []
    history = bool(HISTORY.search(line))
    found = []

    pairs = truth["factors"] * (truth["factors"] - 1) // 2
    for m in PAIR_RE.finditer(line):
        n = as_int(m.group(1))
        if n is not None and n != pairs and not history:
            found.append(("pairwise-count",
                          f'"{m.group(0)}" but {truth["factors"]} factors need {pairs} pairwise comparisons'))

    for m in FACTOR_RE.finditer(line):
        if "pairwise" in m.group(0).lower():
            continue   # a comparison count, not a factor count - handled above
        n = as_int(m.group(1))
        if n is not None and n >= 3 and n != truth["factors"] and not history:
            found.append(("factor-count",
                          f'"{m.group(0)}" but factors.py has {truth["factors"]}'))
    for m in FACTOR_TH.finditer(line):
        n = int(m.group(1))
        if n >= 3 and n != truth["factors"] and not history:
            found.append(("factor-count",
                          f'"{m.group(0)}" but factors.py has {truth["factors"]}'))

    for m in STOCK_RE.finditer(line):
        raw = next(g for g in m.groups() if g)
        n = int(raw)
        if 50 <= n <= 250 and n != truth["stocks"] and not history:
            found.append(("stock-count",
                          f'"{m.group(0).strip()}" but universe.json has {truth["stocks"]}'))

    for m in MONTHS_RE.finditer(line):
        n = int(m.group(1))
        if not 24 <= n <= 240 or history:
            continue
        if is_page:
            found.append(("months-page",
                          f'"{m.group(0)}" typed into a page - read DATA.calibration.months instead'))
        elif CALIB_CONTEXT.search(line) and n != truth["months"]:
            found.append(("months-doc",
                          f'"{m.group(0)}" but calibration.json measured {truth["months"]} months'))

    if not history:
        for pattern, why in STALE:
            if pattern.search(line):
                found.append(("stale-claim", f'"{pattern.pattern}": {why}'))
    return found


def scan(truth):
    findings = []
    for pattern in SCAN:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            if rel in SKIP:
                continue
            is_page = rel.startswith("app/")
            text = path.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                for rule, msg in check_line(line, truth, is_page):
                    findings.append((rel, i, rule, msg))
    return findings


def selftest():
    t = {"factors": 4, "stocks": 95, "months": 83}
    cases = [
        # (text, is_page, expected rule or None)
        ("SETScout ranks stocks on five transparent factors.", False, "factor-count"),
        ("The same four factors are combined with three weight sets.", False, None),
        ("One of our original five factors was another one negated.", False, None),
        ("Six factors → four. The 1 Sep draft had five.", False, None),
        ("the correlation between two factors", False, None),
        ("เรามี 5 ปัจจัย", False, "factor-count"),
        ("เดิมเรามี 5 ปัจจัย", False, None),
        ("Every day it looks at ~92 big Thai stocks (SET100),", False, "stock-count"),
        ("Ranks 95 SET100 stocks on four transparent factors", False, None),
        ('pipeline diagram said "~92 SET"', False, None),
        ("pipeline diagram shows ~92 SET", False, "stock-count"),
        ("only 4 of 95 tickers had data in 1999", False, None),
        ("measured over 84 months, and the same across almost every score band", True, "months-page"),
        ("measured over ${calMonths()} months", True, None),
        ("hold for 6 to 12 months", True, None),
        ("the calibration covers 84 months of history", False, "months-doc"),
        ("the calibration covers 83 complete months of history", False, None),
        ("168 start-points across 14 years, 96 months apart", False, None),
        ("It's a placeholder formula for now.", False, "stale-claim"),
        ("kept telling readers p_win was a placeholder formula", False, None),
        ("Flat, and the top decile is the lowest of the ten.", False, "stale-claim"),
        ("| Conservative | +1.22 | *re-derive* |", False, "stale-claim"),
        ("five factors on purpose  facts-lint: ignore", False, None),
        ("AHP expert survey. Ten pairwise factor comparisons on the Saaty scale", False, "pairwise-count"),
        ("AHP expert survey. Six pairwise factor comparisons on the Saaty scale", False, None),
        ("experts did 15 pairwise comparisons in the old draft", False, None),
    ]
    failed = 0
    for text, is_page, expected in cases:
        rules = [r for r, _ in check_line(text, t, is_page)]
        ok = (expected in rules) if expected else (not rules)
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  expect {expected or 'nothing':<13} got {rules or 'nothing'}  | {text}")
    print(f"\nselftest: {len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


def main():
    # Windows consoles default to cp1252, which cannot print Thai or arrows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if "--selftest" in sys.argv:
        return selftest()
    truth = load_truth()
    print(f"truth from code: {truth['factors']} factors, {truth['stocks']} stocks, "
          f"calibration over {truth['months']} months")
    findings = scan(truth)
    for rel, line, rule, msg in findings:
        print(f"{rel}:{line}: [{rule}] {msg}")
    if findings:
        print(f"\n{len(findings)} contradiction(s). Fix the text, or mark a deliberate "
              f"line with '{IGNORE}'.")
        return 1
    print("docs and pages agree with the code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
