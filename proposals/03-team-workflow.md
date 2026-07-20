# The Team Operating System
### Most complex inside, easiest outside — how 8 of us actually work

_Workflow proposal for the SETscout + Engine project. The design rule is the
same as the product's: every complicated thing lives in machinery and
contracts; every human touches only simple rituals._

---

## 0. The one rule that makes everything work

**Folder ownership.** Every person owns one folder. You have full power inside
your folder and zero power outside it. Merge conflicts become nearly
impossible, nobody can break anyone else's work, and "who owns this?" is
never a question.

```
datascience-equity-research/
├── proposals/          ← decided together
├── data/               ← Role 1  (prices, fundamentals, the sealed test box)
├── scout/              ← Roles 2–4  (scores, news+LLM, discovery ranking)
├── engine/             ← Roles 5–7  (risk, ML, the referee)
├── translator/         ← Role 8a (the four plain-language templates)
├── webapp/             ← Role 8b (dashboard)
├── strategies/         ← EVERYONE (one Arena rule each, template provided)
├── outputs/            ← machine-written only (nobody edits by hand)
├── paper/              ← one file per role: paper/05-risk-engine.md etc.
└── WORKFLOW.md         ← this document
```

## 1. The contracts (the "most complex" part — and why it makes life easy)

The halves never call each other's code. They exchange **files with fixed
shapes**, so anyone can work independently, test alone, and never be blocked:

**Contract A — scout → engine** (`outputs/discovery_YYYY-MM-DD.csv`)
```
ticker,score,rank,reason_1,reason_2
DELTA.BK,0.81,1,"strong earnings growth","sector momentum"
```

**Contract B — engine → translator** (`outputs/analysis_YYYY-MM-DD.json`)
```json
{"DELTA.BK": {"verdict": "WAIT", "risk_month_pct": -16, "max_weight": 0.23,
              "p_win": 0.54, "because": ["price above long average",
              "no recent spike"]}}
```

**Contract C — translator → webapp** (`outputs/today_YYYY-MM-DD.json`)
```json
{"DELTA.BK": {"verdict_th": "รอก่อน 🟡", "risk_sentence": "...",
              "because_sentence": "...", "trust_label": "..."}}
```

**Contract D — everyone → Arena** (`strategies/<yourname>_<idea>.py`)
— the 10-line template; the runner does all the dangerous parts for you.

If your output matches your contract, your layer is correct *by definition*
from the team's point of view. You can be brilliant or struggling inside your
folder — the contract is all anyone else sees. (This is how real engineering
teams scale, and yes, it goes in the report as system design.)

## 2. The four rituals (the "easiest" part — all any member ever does)

**Ritual 1 — The Loop** (whenever you work): 
```
git pull  →  work ONLY in your folder  →  python check_mine.py  →  git add . && git commit -m "..." && git push
```
`check_mine.py` figures out whose folder changed and validates your contract
file automatically. Green = push. Red = it tells you exactly what shape is
wrong. You never need to understand git beyond these four moves.

**Ritual 2 — Screenshot Friday** (weekly, in LINE): everyone posts ONE image
of their layer doing something — a chart, a table, an error you're proud of
beating. No meeting needed; it's show-and-tell, and it's how we detect who's
stuck without anyone having to confess.

**Ritual 3 — The 20-minute Wednesday** (one call): fixed agenda, timed —
5 min: last week's outputs auto-demo · 10 min: blockers (round-robin, one
sentence each) · 5 min: next week's one-task-per-person. No slides, ever.

**Ritual 4 — The Help Flare** (whenever stuck > 30 minutes): post in LINE:
*"Stuck: [what I tried] → [what happened] → [what I expected]"*. Rule: a
flare is answered within a day, and asking is a contribution, not a
confession — the flare count goes in nobody's grade.

## 3. The weekly heartbeat (machinery runs it, not people)

| Day | What happens | Who lifts a finger |
|---|---|---|
| Mon | `python run_today.py` chains scout→engine→translator→web; outputs land in `outputs/` | nobody (one command, rotating duty) |
| Wed | the 20-minute call | everyone, 20 min |
| Fri | Screenshot Friday + Arena leaderboard rerun posts to LINE | everyone, 2 min |
| Sun | integrator (Pon) reviews the week, updates `TASKS.md`, posts the week summary | one person |

## 4. Definition of done (per layer — fill-in-the-blank, not essay)

Your layer is DONE when its folder contains:
- [ ] the code, runnable by `python <yourfolder>/run.py`
- [ ] your contract file produced correctly (check_mine.py green)
- [ ] `README.md` from the template: *what it does / how to run / what I
      learned / one limitation I know about*
- [ ] your `paper/NN-yourlayer.md` section (template: half a page — what,
      why, how, result, limitation)
- [ ] your Q&A card: the 3 questions you'd get + your answers
- [ ] your Arena rule in `strategies/`

Six checkboxes. When they're ticked, you're presentation-ready by
construction — the report and the Q&A prep *are* the checklist.

## 5. The honesty rails (non-negotiable, they protect the grade)

1. **The sealed box stays sealed** — test-window data is touched once, at the
   end, ceremonially, all 8 present (it's a fun moment, actually).
2. **Every experiment is logged** — one line in `outputs/trial_log.md` per
   idea tried. The luck-bar rises with the count; hiding trials is the one
   sin the referee can't forgive.
3. **No force-push, no editing `outputs/` by hand, no touching folders you
   don't own** — check_mine.py enforces all three.
4. **The AI policy** (we all use Claude/GPT — let's be adults about it): AI
   may draft anything, but *you must run it, understand it, and be able to
   explain every line you commit.* If you can't explain it, delete it.
   Q&A day is the enforcement mechanism, and it is merciless.

## 6. Task flow (no Jira, no Notion, no ceremony)

One file: `TASKS.md` — three columns (NOW / NEXT / DONE), one line per task,
name attached. The Sunday integrator gardens it. GitHub Issues only for bugs
that cross folder boundaries. That's the whole system; anything heavier dies
of neglect in student teams.

## 7. Presentation & report assembly (already half-done by the rituals)

- The **report** assembles itself: `paper/00-intro.md` + everyone's section
  (written via checkbox 4 over the weeks, not in a panic at the end) +
  `paper/99-conclusion.md`. Integrator stitches, converts to Word, everyone
  reads once.
- The **presentation** is the pipeline in order — each person's 90 seconds is
  their README's "what/why/result" said aloud, with their Friday screenshot
  as the slide. The finale is live: `run_today.py` on stage, today's real
  list, click a stock, the four sentences appear.
- Two rehearsals, calendar-blocked now: **Aug 13** and **Aug 20**.

## 8. Calendar to the deadline (⏰ 28 Aug)

| Week | Milestone |
|---|---|
| Jul 21 | roles claimed, folders created, contracts frozen, check_mine.py live |
| Jul 28 | every layer produces its contract file (even if crude); Arena rules in |
| Aug 4 | end-to-end `run_today.py` works; paper sections ≥ half-drafted |
| Aug 11 | polish + live-diary week (the system runs daily, we log it publicly) |
| Aug 13 & 20 | rehearsals |
| Aug 18–27 | buffer, final report, submit EARLY |

---

*Why this works, in one line: the contracts make us independent, the rituals
make us synchronized, the rails make us honest, and the checklist makes the
deliverables build themselves while we work.*
