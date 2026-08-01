# SETScout — Expert Questionnaire: AHP Factor Weights (primary data · Stream 1 ⭐)

> Goal: turn expert judgment into the **numeric weights** SCOUT uses to score
> stocks — defensibly, with a consistency check.
> Format: 20–30 min, in person or call. Target: **6–10 experts** (finance
> lecturers, CFA holders, SET analysts, fund managers).
> Output per expert: a weight for each factor + a Consistency Ratio (CR).
> Team weights = geometric mean of all experts' weights.

---

## Consent

> Part of *SETScout*, a student research project. ~25 min. Your responses inform
> an academic model; you may be cited as an expert contributor (or stay anonymous
> — your choice). Data handled under Thai PDPA. ⬜ Agree · Cite me as: ⬜ named ⬜ anonymous

---

## The 6 factors we are weighting

We score each Thai stock on six factors. Your job: tell us **how important each
is for deciding a stock is *worth investigating*** (not "will go up").

| # | Factor | Plain meaning | Example metrics |
|---|---|---|---|
| V | **Value** | Is it cheap vs its fundamentals? | P/E, P/B, dividend yield |
| Q | **Quality** | Is the business sound & profitable? | ROE, net margin, low debt |
| G | **Growth** | Is it growing? | revenue & EPS growth |
| M | **Momentum** | Is the market already favouring it? | 6–12 mo relative return |
| H | **Financial Health / Risk** | Can it survive a bad year? | D/E, liquidity, earnings stability |
| S | **Sentiment** | What does recent news/mood say? | news sentiment score |

*(If you feel a factor is missing or redundant, note it at the end — that's data too.)*

---

## How AHP works (30-second version)

You compare factors **two at a time**. For each pair, pick which is more important
and by how much, on this scale:

`1 = equal · 3 = moderately more · 5 = strongly more · 7 = very strongly · 9 = extremely`
*(2,4,6,8 = in between. We convert your 15 answers into one weight per factor and
check they're internally consistent — CR < 0.1 means coherent.)*

---

## The 15 pairwise comparisons

> For each row: **circle the factor that matters more**, then **write the intensity (1–9)**.
> If they're equal, write 1.

| Pair | More important? (circle) | Intensity 1–9 |
|---|---|---|
| Value ↔ Quality | V / Q | ___ |
| Value ↔ Growth | V / G | ___ |
| Value ↔ Momentum | V / M | ___ |
| Value ↔ Health | V / H | ___ |
| Value ↔ Sentiment | V / S | ___ |
| Quality ↔ Growth | Q / G | ___ |
| Quality ↔ Momentum | Q / M | ___ |
| Quality ↔ Health | Q / H | ___ |
| Quality ↔ Sentiment | Q / S | ___ |
| Growth ↔ Momentum | G / M | ___ |
| Growth ↔ Health | G / H | ___ |
| Growth ↔ Sentiment | G / S | ___ |
| Momentum ↔ Health | M / H | ___ |
| Momentum ↔ Sentiment | M / S | ___ |
| Health ↔ Sentiment | H / S | ___ |

---

## Qualitative follow-up (the "why" — for the report & the "because" sentences)

1. Which factor did you weight highest, and why?
2. For a **beginner** retail investor specifically, would you weight anything
   differently than for a pro? How?
3. Is there a factor here you'd **drop**, or one we're **missing**?
4. A red flag that should make the system say **"Not now"** regardless of score?
5. Anything about the Thai market (SET) that makes a factor behave differently
   than in the US?

---

## How we turn this into weights (team-side note)

1. Build each expert's 6×6 comparison matrix from their 15 answers (reciprocals fill the mirror).
2. Weight vector = normalized principal eigenvector (or the row-geometric-mean shortcut).
3. Consistency Ratio (CR): compute λmax → CI = (λmax−n)/(n−1) → CR = CI / RI(6=1.24).
   **CR < 0.10 = keep; ≥ 0.10 = go back to that expert.**
4. Final SCOUT weights = **geometric mean** of the kept experts' weight vectors, re-normalized.
5. Report: the weight table + mean CR + the qualitative rationale. *That's the primary-data contribution.*
