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
    factor names      FACTORS                      engine/factors.py
    stock count       len(stocks)                  engine/universe.json

Then every current-tense doc and page is scanned for statements that disagree,
and so are the docstrings of the Python in engine/, tools/ and research/ - a
docstring is documentation too, and research/ahp_analyze.py's still promised a
5x5 matrix and an --apply flag that no longer existed.

RULES
-----
  factor-count   "N factors" / "N ปัจจัย" where N >= 3 and N != len(FACTORS)
  stock-count    "N stocks|tickers|SET|หุ้น" where 50 <= N <= 250 and N != stock count
  retired-factor a current-tense line calling "growth" or "value" one of the
                 engine's factors. value went on 2026-09-09, growth on
                 2026-09-16 - both are in FACTORS' history, not in FACTORS
  pairwise-count "N pairwise" comparisons where N != F x (F-1) / 2 - the AHP survey
                 size follows the factor count (its first real catch: REPORT 9 still
                 said "ten", the five-factor number)
  survey-factor  an AHP comparison row ("| 1.1 | Momentum <-> Growth |") or a row of
                 research/ahp_responses_template.csv naming anything but FACTORS.
                 Added 21 Sep 2026, when the unsent survey was found still asking
                 experts to weigh Growth, five days after the engine dropped it
  matrix-size    "N x N matrix" or "RI = ... for n = N" where N != F
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
edit), proposals/ (the original plan, kept as written), and this file's own
docstring, which quotes the mistakes it looks for. Python comments are not read,
only docstrings.

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
SCAN_PY = ["engine/*.py", "tools/*.py", "research/*.py"]      # docstrings only
SKIP = {"docs/CHANGELOG.md", "docs/HANDOFF.md", "tools/facts_lint.py"}
TEMPLATE = "research/ahp_responses_template.csv"

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
RETIRED = {"growth": "2026-09-16, replaced by roe", "value": "2026-09-09, it was momentum negated"}
RETIRED_RE = re.compile(
    r"\b(growth|value)\b(?=[^.]{0,60}\bfactors?\b)|\bfactors?\b(?=[^.]{0,60}\b(growth|value)\b)", re.I)
PAIR_RE = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b"
    r"\s+(?:[A-Za-z-]+\s+){0,1}?pairwise\b", re.I)
RETIRED_ROW = re.compile(r"^\s*\|\s*\*\*(growth|value)\*\*", re.I)     # a factor-table row
SURVEY_ROW = re.compile(r"^\s*\|[^|]*\|\s*([A-Za-z]+)\s*(?:↔|<->)\s*([A-Za-z]+)\s*\|")
MATRIX_RE = re.compile(r"\b(\d+)\s*[x×]\s*(\d+)\b(?=[^.]{0,30}\bmatri)"
                       r"|\bRI\s*=\s*[\d.]+\s+for\s+n\s*=\s*(\d+)", re.I)

STALE = [
    (re.compile(r"placeholder formula", re.I),
     "p_win was removed outright on 2026-09-16 - the app publishes no hit rate at all"),
    (re.compile(r"(shows?|displays?|publishes?)\s+(?:a\s+|the\s+)?(hit rate|p_win|trust label|confidence figure)", re.I),
     "the app no longer shows any hit rate, p_win or trust label"),
    (re.compile(r"top decile (?:is |was )?the lowest", re.I),
     "re-measured on four factors, the top decile is not the lowest (noise, p = 0.53)"),
    (re.compile(r"wire calibration", re.I),
     "calibration.json is gone - backtest.py reports the up-rate as a finding, "
     "and nothing reads it at runtime"),
    (re.compile(r"\*re-derive\*", re.I),
     "REPORT 3.4 ranks have been re-derived"),
    (re.compile(r"barely distinguishable", re.I),
     "balanced is no longer a copy of conservative (REPORT 7)"),
    (re.compile(r"genuinely in the middle", re.I),
     "balanced still leans cautious - do not overclaim"),
    (re.compile(r"not yet backtested|ยังไม่ผ่านการทดสอบย้อนหลัง", re.I),
     "backtested on prices back to 1999 - REPORT 5 and the blind test"),
    (re.compile(r"factors are price proxies|v2 (?:adds|จะเพิ่ม)|ปัจจัยเป็น proxy จากราคา", re.I),
     "ROE has been a factor read from company accounts since 2026-09-16"),
    (re.compile(r"sector[- ]?neutrali[sz]|sector[- ]adjusted|(?:its own|their own) sector peers|"
                r"judged against (?:its own )?sector|within sector|เทียบกับหุ้นในกลุ่มเดียวกัน", re.I),
     "sector neutralisation was dropped on 2026-09-21 (trial 82) - scores are z-scored across all 95"),
]

# The two sealed one-shots keep testing the model they were registered against,
# which still sector-neutralised. Their docstrings say so correctly, so the
# sector rule alone is waived for them - every other rule still applies.
SEALED_OLD_MODEL = {"engine/blind_test.py", "engine/backtest_sizing.py"}


def load_truth():
    sys.path.insert(0, str(ENGINE))
    from factors import FACTORS  # noqa: E402 - factors.py has no imports of its own
    uni = json.loads((ENGINE / "universe.json").read_text(encoding="utf-8"))
    return {"factors": len(FACTORS), "names": list(FACTORS),
            "stocks": len(uni["stocks"])}


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
        part = re.match(r"~?\d{2,3}\s+of\s+(\d{2,3})\b", m.group(0).strip())
        if part and int(part.group(1)) == truth["stocks"]:
            continue    # "92 of 95 stocks" counts part of the universe, not its size
        if 50 <= n <= 250 and n != truth["stocks"] and not history:
            found.append(("stock-count",
                          f'"{m.group(0).strip()}" but universe.json has {truth["stocks"]}'))

    for m in MATRIX_RE.finditer(line):
        a, b, n = m.group(1), m.group(2), m.group(3)
        size = int(n) if n else (int(a) if a == b else None)
        if size is not None and size != truth["factors"] and not history:
            found.append(("matrix-size",
                          f'"{m.group(0).strip()}" but {truth["factors"]} factors make a '
                          f'{truth["factors"]}x{truth["factors"]} matrix'))

    m = SURVEY_ROW.search(line)
    if m and not history:
        for name in (m.group(1), m.group(2)):
            if name.lower() not in truth["names"]:
                found.append(("survey-factor",
                              f'survey row compares "{name}", but factors.py has '
                              f'{", ".join(truth["names"])}'))

    if not history:
        m = RETIRED_ROW.search(line)
        if m and m.group(1).lower() not in truth["names"]:
            name = m.group(1).lower()
            found.append(("retired-factor",
                          f'a factor table lists "{name}", retired {RETIRED[name]}'))
        for m in RETIRED_RE.finditer(line):
            name = (m.group(1) or m.group(2)).lower()
            if name in truth["names"]:
                continue        # still live - nothing to flag
            found.append(("retired-factor",
                          f'"{name}" is written as a factor, but it was retired '
                          f'({RETIRED[name]}) and factors.py now has '
                          f'{", ".join(truth["names"])}'))

    if not history:
        for pattern, why in STALE:
            if pattern.search(line):
                found.append(("stale-claim", f'"{pattern.pattern}": {why}'))
    return found


def docstring_lines(source):
    """(line number, text) for every line of every docstring in a Python source."""
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                d = body[0].value
                src = source.splitlines()[d.lineno - 1:d.end_lineno]
                out += [(d.lineno + k, text) for k, text in enumerate(src)]
    return out


def template_findings(rows, truth):
    """Rows of the AHP answer template must only name live factors."""
    found = []
    for i, r in enumerate(rows, 2):
        for col in ("left", "right", "winner"):
            v = (r.get(col) or "").strip().lower()
            if v and v != "equal" and v not in truth["names"]:
                found.append((i, "survey-factor", f'{col} "{v}" is not one of {", ".join(truth["names"])}'))
    return found


def scan(truth):
    findings = []
    for pattern in SCAN + SCAN_PY:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            if rel in SKIP:
                continue
            is_page = rel.startswith("app/")
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = docstring_lines(text) if rel.endswith(".py") else enumerate(text.splitlines(), 1)
            for i, line in lines:
                for rule, msg in check_line(line, truth, is_page):
                    if rel in SEALED_OLD_MODEL and rule == "stale-claim" and "sector" in msg:
                        continue
                    findings.append((rel, i, rule, msg))
    template = ROOT / TEMPLATE
    if template.exists():
        import csv
        with template.open(encoding="utf-8-sig", newline="") as f:
            for i, rule, msg in template_findings(list(csv.DictReader(f)), truth):
                findings.append((TEMPLATE, i, rule, msg))
    return findings


def selftest():
    t = {"factors": 4, "stocks": 95, "names": ["momentum", "roe", "quality", "health"]}
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
        ("(66-92 of 95 stocks have history, versus 37-62 pre-2015)", False, None),
        ("92 of 94 stocks are covered", False, "stock-count"),
        ("hold for 6 to 12 months", True, None),
        ("168 start-points across 14 years, 96 months apart", False, None),
        ("The four factors are momentum, growth, quality and health.", False, "retired-factor"),
        ("The four factors are momentum, roe, quality and health.", False, None),
        ("growth was removed as a factor on 16 Sep", False, None),
        ("the growth of the dataset is not a factor here", False, "retired-factor"),
        ("a factor that measures value", False, "retired-factor"),
        ("ROE is the one factor that is not a price measure", False, None),
        ("It's a placeholder formula for now.", False, "stale-claim"),
        ("the card shows a hit rate under the risk figure", False, "stale-claim"),
        ("the app used to show a trust label", False, None),
        ("kept telling readers p_win was a placeholder formula", False, None),
        ("Flat, and the top decile is the lowest of the ten.", False, "stale-claim"),
        ("| Conservative | +1.22 | *re-derive* |", False, "stale-claim"),
        ("five factors on purpose  facts-lint: ignore", False, None),
        ("AHP expert survey. Ten pairwise factor comparisons on the Saaty scale", False, "pairwise-count"),
        ("AHP expert survey. Six pairwise factor comparisons on the Saaty scale", False, None),
        ("experts did 15 pairwise comparisons in the old draft", False, None),
        ("| 1.1 | Momentum ↔ Growth | M / G | ____ |", False, "survey-factor"),
        ("| 1.1 | Momentum ↔ ROE | M / R | ____ |", False, None),
        ("| **Growth** การเติบโต | Is it trending up over a longer span? |", False, "retired-factor"),
        ("| **ROE** | Does the business earn well on its owners' money? |", False, None),
        ("It builds each 5×5 matrix, derives priorities", False, "matrix-size"),
        ("It builds each 4×4 matrix, derives priorities", False, None),
        ("computes CR against RI = 1.12 for n = 5", False, "matrix-size"),
        ("computes CR against RI = 0.90 for n = 4", False, None),
        ("a 10x10 grid of charts", False, None),
        ("Not yet backtested", True, "stale-claim"),
        ("Factors are price proxies — v2 adds fundamentals (P/E, ROE)", True, "stale-claim"),
        ("it said Not yet backtested before August", True, None),
        ("Each factor is z-scored and sector-neutralised", False, "stale-claim"),
        ("a stock is judged against its own sector peers", True, "stale-claim"),
        ("Taking PTT on 1 September 2026, sector-adjusted:", False, "stale-claim"),
        ("Until 21 Sep the scores were also sector-neutralised", False, None),
    ]
    failed = 0
    for text, is_page, expected in cases:
        rules = [r for r, _ in check_line(text, t, is_page)]
        ok = (expected in rules) if expected else (not rules)
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  expect {expected or 'nothing':<13} got {rules or 'nothing'}  | {text}")
    # docstrings are read; code and comments are not
    src = 'def f():\n    """Scores on five factors."""\n    x = "five factors"  # five factors\n'
    got = [i for i, text in docstring_lines(src) for _ in check_line(text, t, False)]
    ok = got == [2]
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  docstring line 2 flagged, code and comment ignored  (got lines {got})")
    # the answer template must name live factors only
    rows = [{"left": "momentum", "right": "growth", "winner": "growth"},
            {"left": "momentum", "right": "roe", "winner": "equal"}]
    got = [(i, r) for i, r, _ in template_findings(rows, t)]
    ok = got == [(2, "survey-factor"), (2, "survey-factor")]
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  template row naming growth flagged twice, clean row passes  (got {got})")
    total = len(cases) + 2
    print(f"\nselftest: {total - failed}/{total} passed")
    return 1 if failed else 0


def main():
    # Windows consoles default to cp1252, which cannot print Thai or arrows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if "--selftest" in sys.argv:
        return selftest()
    truth = load_truth()
    print(f"truth from code: {truth['factors']} factors "
          f"({', '.join(truth['names'])}), {truth['stocks']} stocks")
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
