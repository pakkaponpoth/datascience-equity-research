# 📋 SETScout — Changelog

*What changed, why, and how to check it. Newest first.*

---

## 2026-08-31 (later) — Blind test: the aggressive edge does not replicate

**สรุปสั้น ๆ** เราดูข้อมูลชุดเดิมมาแล้วประมาณ 15 รอบ แล้วเจอว่า aggressive ชนะ — ซึ่งเชื่อไม่ได้ เพราะเลือกผลที่สนใจ*หลัง*เห็นข้อมูลแล้ว จึงทำ blind test: เขียนเงื่อนไขตัดสินล่วงหน้า แล้วทดสอบบนช่วง 1999–2014 ที่ไม่เคยดูแยกมาก่อน **ผล: ไม่ replicate** (luck bar 81% ต่ำกว่าเกณฑ์ 90% ที่ตั้งไว้ก่อน และชนะแค่ 2/5 ช่วง)

### Why

Five scripts x three profiles over one decade is roughly **fifteen looks at the same data**.
We then reported the `aggressive` profile beating buy-and-hold at a 96% luck bar. That is
not evidence — we chose which result to be interested in *after* seeing it.

### Design (written into `blind_test.py` before the first run)

| | |
|---|---|
| Sealed period | score months **1999-01 → 2014-12**, never examined in isolation |
| Development period | 2016-01 → now — examined ~15 times, shown only for contrast |
| Gap | 2015, so a 12-month hold from Dec-2014 cannot touch the dev window |
| Weights | **frozen**, copied verbatim from `run_today.py` |
| Decision rule | REPLICATES = beats B&H **and** luck bar ≥ 90% |

### Result — `reports/blind_test.md`

| Profile | Sealed 12-mo | vs B&H | Luck bar | Verdict |
|---|---|---|---|---|
| conservative | +57.9% | +16.9 | 100% | replicates |
| balanced | +60.2% | +19.1 | 100% | replicates |
| **aggressive** | **+44.1%** | **+3.0** | **81%** | **weak — fails the pre-set bar** |

- 81% is under the 90% we committed to, and well under the **96.6%** Šidák bar for three profiles.
- Non-overlapping blocks: aggressive beat B&H in **2 of 5** three-year blocks (40%, below a coin flip).
- Re-measured on this longer history the development window gives aggressive **+0.2 pts, 56% luck bar** — the original "+1.8, 96%" did not survive even a change in window definition.

**A pre-registered test refuted a finding we had already half-believed. Present that.**

### Two warnings

1. **Do not now claim the defensive profiles are the edge.** They post a 100% luck bar in the
   sealed period and fail in development — but we did not predict that, we found it by looking.
   Announcing it would repeat the exact error one period later. It earns its own future test.
2. **Sealed-period buy-and-hold averages +41.1% per 12 months — that number is 4.4x reality.**
   Measured decomposition (Protocol spotted it was implausible; this is the check):

   **Two different things are both called "annual return".** An *average of one-year returns*
   (168 overlapping windows, averaged) is not a *CAGR* (the steady rate that turns start value
   into end value). For volatile series the first is always larger. +41.1% is the first kind.

   | Measure | Annual | Type |
   |---|---|---|
   | reported in the blind test | +41.1% | avg of 12-mo returns — **not** a growth rate |
   | basket compounded, **with** dividends | +33.3% | CAGR |
   | basket compounded, **price only** | +26.6% | CAGR — comparable to the index |
   | real SET index, price only | **+9.4%** | CAGR |

   **Correction to an earlier draft**, which blamed 18.5 pts on survivorship:
   - **+6.7 pts/yr was just dividends** — the basket was dividend-adjusted, `^SET.BK` is
     price-only. Apples-to-oranges on my part, not bias.
   - **+17.1 pts/yr is the real like-for-like gap**, and even that is still *two* things mixed:
     survivorship **plus** equal-weight-vs-cap-weight tilt (equal weighting favours smaller
     names, which historically return more). Separating them needs market-cap history we lack.

   The basket CAGR also swings **+27% to +33%** depending which stocks you require history for.
   A number that moves 6 points on a sample-construction choice is not a number to quote.
   Not one lucky stock either: median 12-mo +36.2% vs mean +41.1% — the whole basket is lifted.

3. **The bias is NOT neutral between profiles — this is the important one.** Survivorship
   selects for companies that did not blow up, which is exactly what **quality** and **health**
   score. Conservative puts 70% of its weight on those two, balanced 44%, aggressive 15%. So a
   survivors-only sample structurally flatters precisely the profiles that scored 100% luck
   bars. Their "replication" is probably a sample artifact — a second, stronger reason not to
   claim it.

   **What still holds:** the luck bar draws random books from the same biased universe, so the
   aggressive comparison stays internally valid, and the recent-decade edge did not reappear.
   That conclusion survives. The levels do not. Fixing levels properly needs point-in-time
   index membership, which we do not have — saying so is worth more than assuming it away.

### Files

```
setscout/blind_test.py          NEW - pre-registered, run once
setscout/reports/blind_test.md  NEW - the preserved result
```

---

## 2026-08-31 — Backtests now leave evidence behind

**สรุปสั้น ๆ** ตัวเลข backtest ทั้งหมดเคยอยู่แค่ใน console แล้วหายไป ตอนนี้ทุกสคริปต์เขียนผลลง `reports/` พร้อมวันที่รันและพารามิเตอร์ + แก้ threshold ที่ผิด + ลิงก์หน้า onboard แล้ว

### 1. Every backtest writes a reproducible report

**Why.** Only `backtest.py` saved anything (`calibration.json`), and even it didn't save its headline numbers. `backtest_hold.py`, `backtest_long.py`, `backtest_costs.py` and `backtest_profiles.py` wrote **nothing** — every result lived in console scrollback. The written report is the biggest grade component and its entire evidence base was ephemeral and uncitable.

**What changed.** New `reportlib.py`. One line per script:

```python
from reportlib import capture, load_universe
capture("backtest_hold", "Hold test - buy the picks and hold H months", {...})
```

It tees stdout *and* stderr into `reports/<slug>.md` with a run stamp, elapsed time, the parameters, and a reproduce command. Console behaviour is unchanged, and a crashed run still writes a report containing the traceback.

`reportlib.load_universe()` also points every backtest at **`universe.json`** instead of `today.json` — previously a backtest could silently run on a different set of stocks than the engine was scoring.

**Results now on disk:** `reports/backtest.md`, `backtest_hold.md`, `backtest_long.md`, `backtest_costs.md`, `backtest_profiles.md`.

### 2. The finding got more interesting

Re-run on the corrected 95-stock universe. **Calibration is flatter than ever** — deciles run 44.2% to 50.4% with the *top* decile the worst at 44.2%, n ≈ 700–790 per bucket. The score does not predict direction, confirmed on fresh data.

But the profile split is not uniform:

| Test | Conservative | Balanced | Aggressive | Buy & hold |
|---|---|---|---|---|
| 12-month hold, avg return | +1.2% | +1.7% | **+8.8%** | +7.0% |
| return / risk | 0.08 | 0.11 | **0.51** | — |
| luck bar | 0% | 0% | **96%** | — |
| 10y net after 1% costs | +23% | +16% | **+164%** | +94% |
| full-window CAGR | +22.7% | +23.0% | **+25.2%** | +21.5% |

**The aggressive profile beats buy-and-hold on every horizon tested, with a 96% luck bar.** That is above `backtest.py`'s own "edge looks real" threshold.

**Do not present this as a discovered edge.** Five reasons to distrust it, all of which should be said out loud:

1. **Survivorship bias** — the universe is *today's* SET100 members. The full-window numbers (+16,000%) are obviously inflated by it.
2. **Three profiles tested = three trials.** A 96% luck bar on the best of three is much weaker than 96% on a single pre-registered test.
3. **Overlapping windows** — 73 start-points on 8 years of data are nowhere near independent.
4. **Higher volatility** (17.1% vs 15.1%) — part of the return is simply more risk taken.
5. **It corroborates the sibling repo's null result**, where momentum-style rules were rejected by pre-committed gates.

The honest framing: *the momentum-tilted weighting shows a persistent tilt in this window, and here is why we are not claiming it as an edge.* That is a stronger result than either "it works" or "nothing works".

### 3. The last two UI contradictions are closed

- **Verdict thresholds.** The panel said `≥62 / ≥48`; the engine cuts at the 80th and 45th percentile. Now stated in percentile language, which also matches the stat that changed from `Score /100` to `Rank`: *"Top 20% of the market → Worth a look · 45–80th percentile → Wait · below 45th → Not now."*
- **`onboard.html` is reachable.** A `?` button in the header links to it. It was a good explainer that nothing pointed at.

### Files touched

```
setscout/reportlib.py            NEW - capture() + canonical load_universe()
setscout/backtest*.py            one capture line each; read universe.json
setscout/reports/*.md            NEW - five reproducible result files
setscout/index.html              thresholds corrected, onboard.html linked
setscout/calibration.json        re-measured on the 95-stock universe
setscout/today.json              regenerated
```

---

## 2026-08-30 — Honesty + reliability pass

**สรุปสั้น ๆ (ภาษาไทย)**

แก้ 3 เรื่องที่เจอจากการไล่โค้ด — ไม่ได้แตะ logic การให้คะแนนเลย ผลลัพธ์ที่ validate ไว้แล้วไม่มีอะไรเปลี่ยน

1. **`p_win` เลิกเป็นตัวเลขปลอม** — เดิมคือ `0.44 + 0.22 × คะแนน` (สูตรที่ตั้งขึ้นมาเอง ไต่จาก 44% ถึง 66% ตามอันดับ) ตอนนี้อ่านค่าจริงจาก `calibration.json` ที่ `backtest.py` วัดไว้จาก 84 เดือน — ซึ่ง**แบนราบ ~47% ทุกช่วงคะแนน** แปลว่าคะแนนไม่ได้ทำนายทิศทาง และหน้าเว็บพูดแบบนั้นแล้ว
2. **Workflow จะ fail เสียงดัง** — เดิมถ้า engine พัง มันจะเงียบ ไม่ commit ไม่บอกใคร เว็บเสิร์ฟข้อมูลเก่าไป 21 วันโดยไม่มีสัญญาณ ตอนนี้มี `verify_today.py` ตรวจก่อน commit
3. **แยก `universe.json` ออกมา** — เดิม engine อ่านรายชื่อหุ้นจาก `today.json` ที่ตัวเองเขียนทับ หุ้นที่ดึงไม่สำเร็จครั้งเดียวจะหายถาวร (หายไปแล้ว 4 ตัว) ตอนนี้ได้คืนมา **92 → 95 ตัว**

---

### 1. `p_win` is now measured, not invented

**Why.** `run_today.py` computed `p_win = round(0.44 + s01 * 0.22, 2)` — a straight line off the percentile rank. Verified against all 276 records in the old `today.json`: it matched that formula exactly every time. So the number carried **zero independent information**, the constants were hand-picked, and it was displayed to beginners as "Hit rate" / "โอกาสเข้าทาง" — which reads as an empirical probability.

Worse, `backtest.py` had **already measured the truth** and written it to `calibration.json` on 2026-08-02. Its own docstring says the file exists "so run_today.py can stop faking p_win." It was never wired in.

| Score decile | 0–10 | 30–40 | 60–70 | 80–90 | 90–100 |
|---|---|---|---|---|---|
| **Measured up-rate** (84 months) | 46.5% | 44.7% | 47.4% | 46.0% | **45.2%** |
| **What the app used to show** | 44–46% | 51–53% | 57–59% | 62–64% | **64–66%** |

The real up-rate is **flat at ~47.2%** across every decile, spread 4.5pp, with no gradient. The app was showing it climbing to 66%. The displayed number wasn't merely unvalidated — it was **contradicted by our own measurement**.

**What changed.**
- `run_today.py` reads `calibration.json` and emits `p_win` as the measured up-rate for that stock's decile. Bucketing matches `backtest.py` exactly: `(score*10).clip(0,9)`.
- If `calibration.json` is missing, `p_win` is `null` — never invented. The UI renders `—`.
- `today.json` gained a top-level `calibration` block (source, months, base rate, spread, and a plain-language note) so the site can cite its own evidence.
- `index.html`: the stat label is now **"Past up-rate" / "ราคาขึ้นในอดีต"**, and the trust sentence says the number is flat across score bands and therefore does not predict direction. The old "⚠️ not yet backtested" line is gone — it *has* been backtested, and that's the point.
- The other stat changed from `Score /100` to **`Rank`**. The percentile score is fixed by list position (#1 always read 100), so it looked like a property of the stock when it's a property of the position. `#1 of 95` is honest and makes personalisation visible.

**Check it.** `python run_today.py` prints `p_win: CALIBRATED from calibration.json (84 months, base rate 47.2%)`. Open any card — the top-ranked stock now reads ~45%, not 66%.

**This is the project's thesis, rendered in the product.** A grader who clicks one card sees an honest null result rather than a fabricated confidence figure.

---

### 2. The daily workflow now fails loudly

**Why.** `.github/workflows/refresh-setscout.yml` runs daily at 11:00 UTC. The commit step is conditional, so a crashed engine would commit nothing and report nothing — a silent failure path with no alarm on it.

> **Correction, 1 Sep 2026.** This entry originally claimed the Action had been dead since 9 August and that the site served stale data for 21 days. **That was wrong.** It ran every single day, 10–31 August, 22 commits. The diagnosis came from a local git log that was 22 commits behind because it had never been fetched. What *was* true: the live site ran the **old engine** (92 stocks, fabricated `p_win: 0.66`) until the 1 Sep push. The guard below is still worth having, but it closes a hypothetical hole rather than an observed outage.

The commit step is `git diff --staged --quiet || git commit`. If the engine crashes, there's nothing staged, so the workflow "succeeds" with no commit, no error, and no notification. The site just keeps serving stale data forever.

**What changed.** New `verify_today.py`, run after the engine and **before** the commit. It fails the job (exit 1, which GitHub emails about) when:

- fewer than 90% of `universe.json` scored
- `generated` isn't today — the engine didn't actually rewrite the file
- any of the three profiles is missing or has a different row count
- `calibration` is null
- any stock has no price

No third-party imports, deliberately: it has to run even when the engine's own dependencies are what broke.

**Check it.** `python verify_today.py` → `OK - 95 stocks scored, generated 2026-08-30, …`. Tested against a simulated partial fetch (40/95): correctly fails with `only 40/95 stocks scored (42%, need 90%)`.

**Still to diagnose:** *why* it stopped. yfinance runs fine from a local machine, so the likely cause is Yahoo rate-limiting GitHub's runner IPs — a very common failure. **Check the repo's Actions tab → "Refresh SETScout data"**: red X's mean it's failing (read the log); no runs at all means it isn't triggering. If it's rate-limiting, the fix is a retry with backoff, which we can add once the log confirms it.

---

### 3. The universe is its own file now

**Why.** `run_today.py` read its ticker list from `today.json` — the same file it overwrites:

```python
uni = json.load(open(FILE))                       # input
...
"stocks": profiles["balanced"]                    # output, same file
```

Any ticker that failed to fetch **once** disappeared permanently: the next run didn't know it had ever existed. This had already happened — the seed universe in `gen_today.js` has 96 names, `today.json` was down to 92.

**What changed.**
- New **`universe.json`** — canonical, read-only for the engine, with a `retired` section that records deliberate removals rather than losing them.
- `run_today.py` reads it and writes only `today.json`. A failed fetch is skipped for that run, reported by name, and retried tomorrow.
- Falls back to `today.json` with a loud warning on old checkouts.
- Recovered the lost names, and fixed two bad symbols found while checking them:

| Ticker | Action | Evidence |
|---|---|---|
| BANPU | restored | fetches fine, was lost to a transient failure |
| BGRIM2 → **BCPG** | symbol corrected | not a SET symbol; the seed entry's own names read บีซีพีจี / BCPG |
| ORIGIN → **ORI** | symbol corrected | `ORIGIN.BK` 404s; `ORI.BK` is live (Origin Property, ฿1.80) |
| INTUCH | **retired** | genuinely delisted — merged into GULF (2025). Kept in `retired` with a reason |

**Result: 92 → 95 stocks scored, with zero skipped on the latest run.**

**Check it.** `python run_today.py` prints `95 tickers from universe.json`. To add or remove a stock, edit `universe.json` — nothing else.

---

### Not done yet

- **The verdict thresholds in "How we score" are still wrong.** The panel says `≥ 62 → Worth a look, ≥ 48 → Wait` in both languages. The engine cuts at **80 and 45** (confirmed: the BUY band is 80–100, WAIT 46–79). One string edit per language, deliberately left for review.
- `onboard.html` is still orphaned — no page links to it.
- `backtest.py` still prints its headline numbers (strategy vs buy-and-hold, luck bar, Sharpe) to the console and saves only `calibration.json`. Those belong in `reports/`.
- The AHP survey is still the open primary-data work, and the long pole — it depends on other people.

### Files touched

```
setscout/run_today.py       universe + calibration wiring, drop reporting
setscout/index.html         honest trust sentence, Past up-rate, Rank, null guards
setscout/universe.json      NEW - canonical read-only ticker list
setscout/verify_today.py    NEW - health check for the daily refresh
setscout/today.json         regenerated: 95 stocks, calibrated p_win
.github/workflows/refresh-setscout.yml   added the verify step
```

Not pushed — staged locally for review.
