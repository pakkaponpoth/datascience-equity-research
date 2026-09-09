# SETScout — Expert Questionnaire: AHP Factor Weights
# แบบสอบถามผู้เชี่ยวชาญ — น้ำหนักปัจจัยคัดหุ้น

> **Goal:** turn expert judgement into the **numeric weights** SETScout uses to
> score stocks — defensibly, with a consistency check.
> **Format:** 20–30 min, in person or by call. **Target:** 6–10 experts
> (finance lecturers, CFA holders, SET analysts, fund managers).
> **Output per expert:** a weight for each factor, per investor profile, plus a
> Consistency Ratio.

---

## Consent / ความยินยอม

> Part of *SETScout*, a student research project (Data Science 01526125). About
> 25 minutes. Your responses inform an academic model. You may be cited as an
> expert contributor, or stay anonymous — your choice. Data handled under Thai
> PDPA: any name or email is used **only** to follow up on consistency, is never
> published or shared, and is deleted after submission. You may withdraw at any
> time.
>
> ⬜ I agree to participate  ·  Cite me as: ⬜ named ⬜ anonymous

---

## Why we are asking / ทำไมเราถึงขอความเห็นคุณ

SETScout scores SET100 stocks on five factors. **The weights are currently our
own guesses with no evidence behind them** — nobody has measured that "quality"
should be 40% rather than 35% for a cautious investor. This survey replaces
guesses with judgement from people who know the market.

There are **no right answers.** We want your professional view, and we will
report the **disagreement** between experts as well as the average — the spread
is as much a finding as the mean.

เราต้องการความเห็นเชิงวิชาชีพของคุณ ไม่ใช่คำตอบที่ "ควรจะเป็น"
และเราจะรายงานความ**ไม่**เห็นตรงกันระหว่างผู้ตอบด้วย

---

## ⚠️ Read the factor definitions before answering

Your job is to say how important each factor is for deciding a stock is
**worth investigating** — *not* "will go up".

**All five are computed from price data only.** No revenue, earnings or debt.
Our names are shorthand and may not mean what you would normally assume, so
please judge them **as defined in the right-hand column**.

| Factor | Plain meaning | **What we actually compute** |
|---|---|---|
| **Momentum** โมเมนตัม | Is the market already favouring it? | Return over the past **6 months** |
| **Growth** การเติบโต | Is it trending up over a longer span? | Return over the past **12 months** — *price growth, **not** revenue or EPS* |
| **Value** ราคาเทียบค่าเฉลี่ย | Is it cheap relative to its own recent past? | Price vs its own **200-day average** — ***not** P/E, P/B or dividend yield* |
| **Quality** คุณภาพ | Is it calm rather than wild? | **Annualised volatility** (lower is better) — ***not** ROE, margin or debt* |
| **Health** สุขภาพ | Did it survive bad stretches? | **Worst drawdown** over 1 year — ***not** D/E or liquidity* |

*If you think a factor is missing or redundant, say so at the end — that is data too.*

---

## How AHP works (30-second version)

You compare factors **two at a time**. For each pair, pick which matters more and
by how much:

`1 = equal · 3 = moderately more · 5 = strongly more · 7 = very strongly · 9 = extremely`
*(2, 4, 6, 8 = in between.)*

We convert your answers into one weight per factor and check they are internally
coherent. If you say A > B and B > C but then C > A, that is an inconsistency.

We compute a **Consistency Ratio** and keep responses below **0.10**. If yours is
above, we will come back and ask you to revisit a few rows — routine, not a
failure. **We will report how many responses were excluded**, because hiding that
would misrepresent how strong our result is.

---

# Block 1 — a BALANCED investor  ·  สายสมดุล

> Some experience · 3–5 year horizon · tolerates moderate swings · wants both
> growth and safety.

**Answer this block in full.** Circle the factor that matters more, then write
the intensity.

| # | Pair | More important? | Intensity 1–9 |
|---|---|---|---|
| 1.1 | Momentum ↔ Growth | M / G | ____ |
| 1.2 | Momentum ↔ Value | M / V | ____ |
| 1.3 | Momentum ↔ Quality | M / Q | ____ |
| 1.4 | Momentum ↔ Health | M / H | ____ |
| 1.5 | Growth ↔ Value | G / V | ____ |
| 1.6 | Growth ↔ Quality | G / Q | ____ |
| 1.7 | Growth ↔ Health | G / H | ____ |
| 1.8 | Value ↔ Quality | V / Q | ____ |
| 1.9 | Value ↔ Health | V / H | ____ |
| 1.10 | Quality ↔ Health | Q / H | ____ |

---

# Block 2 — a CAUTIOUS beginner  ·  สายระมัดระวัง

> A 22-year-old beginner · first savings · low risk tolerance · more afraid of
> losing than eager to gain.

**Shortcut:** start from your Block 1 answers and change only what differs for
this investor. Most experts change three or four rows, not ten. Leave a row blank
to mean "same as Block 1".

| # | Pair | More important? | Intensity 1–9 |
|---|---|---|---|
| 2.1 | Momentum ↔ Growth | M / G | ____ |
| 2.2 | Momentum ↔ Value | M / V | ____ |
| 2.3 | Momentum ↔ Quality | M / Q | ____ |
| 2.4 | Momentum ↔ Health | M / H | ____ |
| 2.5 | Growth ↔ Value | G / V | ____ |
| 2.6 | Growth ↔ Quality | G / Q | ____ |
| 2.7 | Growth ↔ Health | G / H | ____ |
| 2.8 | Value ↔ Quality | V / Q | ____ |
| 2.9 | Value ↔ Health | V / H | ____ |
| 2.10 | Quality ↔ Health | Q / H | ____ |

---

# Block 3 — an AGGRESSIVE investor  ·  สายบุก

> Experienced · tolerates high volatility · 5+ year horizon · accepts deep
> drawdowns for growth potential.

Same shortcut: change only what differs from Block 1.

| # | Pair | More important? | Intensity 1–9 |
|---|---|---|---|
| 3.1 | Momentum ↔ Growth | M / G | ____ |
| 3.2 | Momentum ↔ Value | M / V | ____ |
| 3.3 | Momentum ↔ Quality | M / Q | ____ |
| 3.4 | Momentum ↔ Health | M / H | ____ |
| 3.5 | Growth ↔ Value | G / V | ____ |
| 3.6 | Growth ↔ Quality | G / Q | ____ |
| 3.7 | Growth ↔ Health | G / H | ____ |
| 3.8 | Value ↔ Quality | V / Q | ____ |
| 3.9 | Value ↔ Health | V / H | ____ |
| 3.10 | Quality ↔ Health | Q / H | ____ |

---

## Qualitative follow-up

*The "why" — this feeds the report and the plain-language "because" sentences
the app shows users.*

1. Which factor did you weight highest, and why?
2. For a **beginner** specifically, would you weight anything differently than
   for a professional? How?
3. Is there a factor here you would **drop**, or one we are **missing**?
   *(We removed a "Sentiment" factor from an earlier draft because the engine
   does not compute it. Should it be added?)*
4. What is a **red flag** that should make the system say "Not now" regardless
   of score?
5. Is there anything about the Thai market specifically that makes a factor
   behave differently than it would in the US?
6. Our factors are all price-based, so "quality" is really low volatility and
   "health" is really shallow drawdown. **How much does that limitation worry
   you**, and which fundamental would you add first?

---

## About you / ข้อมูลผู้ตอบ

- Years of market experience: ______
- Role (analyst, fund manager, lecturer, retail investor…): ____________________
- Happy to be contacted if your answers look inconsistent? ⬜ yes ⬜ no

**Short on time?** Block 1 alone is genuinely useful. The analysis handles
partial responses.

---

## Team-side note — how this becomes weights

1. Enter responses into `research/ahp_responses.csv`:
   `respondent,profile,left,right,winner,strength`
   (template with a worked example: `ahp_responses_template.csv`)
2. Run `python research/ahp_analyze.py`
3. It builds each 5×5 matrix, derives priorities by **row geometric mean**,
   computes CR against **RI = 1.12 for n = 5**, drops CR ≥ 0.10 and says who and
   why, then aggregates survivors by **geometric mean of judgements (AIJ)**.
4. It also prints the **min–max spread across respondents**. That spread becomes
   the perturbation range for sensitivity analysis — so we never have to answer
   *"why ±10%?"*. Bootstrapping it gives a per-stock top-10 stability figure:
   *"PTT appears in the top 10 under 87% of expert weightings."* That is the
   intended honest replacement for the `p_win` number the app used to invent.
5. **Report all of:** how many responded, how many were dropped and why, the mean
   CR, the weight spread, and the bootstrap stability. The exclusions and the
   disagreement are the primary-data contribution, not embarrassments.

Test the whole pipeline before any real response arrives:
`python research/ahp_analyze.py --demo`

### Changed from the earlier draft (1 Sep 2026)

- **Six factors → five.** The earlier version asked about *Sentiment*, which the
  engine does not compute, and defined Value as P/E, Quality as ROE and Health as
  D/E — none of which the engine computes either. Weights collected for P/E and
  ROE cannot be applied to volatility and drawdown. Question 3 above now asks
  whether Sentiment should be added, so the idea is not lost.
- **One block → three**, because SETScout serves three risk profiles and needs
  three weight sets. Blocks 2 and 3 use a copy-and-adjust shortcut to keep the
  survey near its original length.
- Consent, citation options and the qualitative follow-up are kept from the
  earlier draft.
