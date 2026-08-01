# 🧭 SETScout — Project Handoff

> Everything a new teammate needs to carry this project onward. Read top-to-bottom once,
> then use it as a reference. Written by Pim + Claude, Jul 2026.

---

## 0. TL;DR + all the links

**SETScout** = an *Explainable Investment Decision Support System (EIDSS)* for the **Thai stock market (SET)**. It doesn't predict prices or trade — it **surfaces SET stocks worth *researching*** and explains **why** in 4 plain sentences, always with the risk attached. Senior Data-Science-in-Finance project · **deadline 28 Aug 2026**.

| Thing | Link |
|---|---|
| 🌐 **Live website (working demo)** | https://oksoimcodingnow.github.io/atlas/setscout/ |
| 🗺️ **Visual system map** (open this first) | https://oksoimcodingnow.github.io/atlas/library/setscout-map.html |
| 📦 **Project repo** (Pon's) | https://github.com/pakkaponpoth/datascience-equity-research |
| 🧑‍💻 Website + docs repo (Pim's Atlas) | https://github.com/oksoimcodingnow/atlas → `/setscout/` |
| 📋 Primary-data instruments | `research/investor-survey.md`, `research/expert-ahp.md` |
| Proposals (read in order) | `proposals/01-engine…`, `02-…integrated`, `03-team-workflow` |

**The one rule for everything:** *most complex inside, simplest outside.* Every hard thing hides in machinery + file contracts; every human only touches simple rituals.

---

## 1. What it is — and the framing you must NOT break ⚖️

- It **finds** promising SET stocks (discovery), it does **not** promise profit.
- **Legal:** it's an **educational/research project, NOT investment advice.** Keep the disclaimer everywhere, use **soft wording** ("worth a look / wait / not now" — never "buy this / good stock"), keep it **free/non-commercial**. In Thailand, paid public stock recommendations = SEC-regulated advisory. As a non-commercial class project with disclaimers, you're fine — **don't cross into a paid public "buy X" service.**

---

## 2. The core design — "the honest engine"

**What a user ever sees = 4 sentences** (this is the whole product surface):
1. **Verdict** — Worth a look ✅ / Wait 🟡 / Not now 🔴 (honest enough to say "none today")
2. **Risk in baht** — "a normal-bad month ≈ −16%, so put at most ฿23 of every ฿100"
3. **Because** — "price is above its long average and hasn't just spiked"
4. **Trust label** — "tested on 10 yrs; when we say 60% it happened ~60%; we don't promise profit"

**8 internal jobs** (only #5 is AI — and its job is to say *"not sure"*): ① data keeper (+ frozen holdout) · ② rule writer (momentum + mean-reversion) · ③ backtest w/ fees · ④ Monte-Carlo risk → VaR + position size · ⑤ humble ML "second opinion" · ⑥ **referee** (walk-forward × 16 windows + a **luck bar** vs random ideas) · ⑦ translator (the 4 sentences) · ⑧ webapp.

**Strategy Arena** — every teammate writes ONE 10-line rule → identical honest machinery → leaderboard vs buy-and-hold. **Most rules lose; that's the lesson** (and the honest research finding).

---

## 3. Architecture — batch precompute + file contracts

**The engine runs AHEAD OF TIME, not when a user clicks.** It writes a file; the website reads that file. They never call each other live.

```
On your machine (once/day):  run_today.py  →  scout → engine → translator  →  outputs/today.json
Public website (anytime):    just READS today.json and shows it   (instant, no compute)
```

- **Users never wait** — the recommendations were precomputed.
- **Build in parallel:** freeze the file *shape* (the contracts), then everyone builds against a **mock file** independently. The website was built before any engine exists — that's the point.
- **Personalization** (risk quiz) happens **in the browser** on the precomputed data (localStorage) — no engine call.
- **You only run it daily during the ~1 "live-diary" week + live on stage.** Not a forever chore. Optionally automate with a GitHub Action.

**The contracts** (from `03-team-workflow.md`):
- A `scout → engine` : `outputs/discovery_YYYY-MM-DD.csv`
- B `engine → translator` : `outputs/analysis_YYYY-MM-DD.json`
- C `translator → webapp` : `outputs/today_YYYY-MM-DD.json`
- D `everyone → Arena` : `strategies/<name>_<idea>.py`

---

## 4. Team operating system (from proposal 03 — already excellent)

- **Folder ownership:** 1 person = 1 folder, full power inside, zero outside → no merge conflicts. `data/ scout/ engine/ translator/ webapp/ strategies/ outputs/ paper/`.
- **4 rituals:** ① The Loop (`git pull → work in your folder → check_mine.py → commit/push`) · ② Screenshot Friday (post 1 image in LINE) · ③ 20-min Wednesday call · ④ Help Flare (stuck >30 min → post in LINE).
- **Honesty rails (non-negotiable):** sealed test box opened once at the end · every experiment logged in `outputs/trial_log.md` (the luck-bar rises with the count) · no force-push / no hand-editing `outputs/` / no touching folders you don't own · **AI policy: draft with AI, but run it, understand it, and be able to explain every line — or delete it.**
- **Calendar:** Jul 21 contracts frozen · Jul 28 every layer emits its file · Aug 4 end-to-end works · Aug 11 live-diary week · Aug 13 & 20 rehearsals · **28 Aug submit.**

---

## 5. The multi-factor model (how stocks get scored)

**6 factors:** **V**alue · **Q**uality · **G**rowth · **M**omentum · financial-**H**ealth/risk · **S**entiment.

**Weights come from experts via AHP** (Analytic Hierarchy Process, Saaty 1980): experts do 15 pairwise comparisons (1–9 scale) → we compute a weight per factor + a **Consistency Ratio** (CR < 0.10 = coherent). Team weights = geometric mean across experts. *(Instrument: `research/expert-ahp.md`. This is the primary-data flagship — say "weights from N experts via AHP, mean CR 0.06" in the defense.)*

**Scoring (illustrative):**
```
score = wQ·Q + wV·V + wM·M + wH·H + wG·G + wS·S      (factors normalized 0–1 across the universe)
verdict:  score ≥ ~0.62 → BUY(worth a look) · ≥ ~0.48 → WAIT · else → AVOID(not now)
```
Change the weights → the ranking genuinely changes. Fully transparent, no black box.

---

## 6. Primary data (your prof's requirement) — 3 streams + the in-site quiz

Primary = data **we collect ourselves** (yfinance/SET/FRED are *secondary*).

1. **⭐ Expert AHP** → the factor **weights** (changes *which stocks* rank). `research/expert-ahp.md`.
2. **Retail-investor survey** → proves the problem + tests if users understand the 4 sentences (changes *the wording/UX*). Uses Lusardi's validated "Big Three" literacy Qs. `research/investor-survey.md`.
3. **Usability/explainability test** → A/B (LLM explanation vs bare numbers) proves the "Explainable" thesis.
4. **In-site risk quiz** (built into the website) → 5 Qs → Conservative/Balanced/Aggressive → **personalizes** the list (re-rank + rescale position size) **and** collects the risk distribution of real users = ongoing primary data.

**Ethics wrapper (all of it):** informed consent · **Thai PDPA** (anonymize, minimal, secure) · pilot each instrument on 3–5 people first · check if the faculty needs a human-subjects review.

**How each feeds the product:** survey finds a sentence 60% misread → **rewrite that sentence**; survey says "trust needs risk shown" → **put risk front-and-center**; AHP weights → **plug into the scorer**. Data you don't act on is wasted — Step 6 is *apply it to the site + quote it in the report.*

---

## 7. Tech stack (lean — fewest moving parts for 8 people)

| Layer | Use | Note |
|---|---|---|
| Core | **Python 3.11** (pandas·numpy·scikit-learn) | scout/engine/translator |
| Fetch | yfinance (`.BK`) · requests+BeautifulSoup · fredapi | |
| Store | **CSV/Parquet, or SQLite** | ❌ **not Postgres** — data is tiny, contracts are files. DBeaver = a *GUI to view* a DB, not a DB. |
| ML | scikit-learn LogisticRegression (calibrated, AUC) | the one "humble" model, fixed seed |
| Explanations | **templates first**, LLM only for flavor | see below |
| Web | **static HTML/JS + GitHub Pages** | reads `today.json`; client-side personalization is trivial |
| Orchestrate | plain `run_today.py` (+ optional GitHub Action) | no Airflow |

**The LLM decision (important):** the LLM is **NOT mandatory.** The 4 sentences are **templates built from the engine's numbers** (see `index.html` `T` object — pure string templates, no AI). The LLM is optional garnish for **news-summary sentiment only**. Use **Ollama** (free, local, offline) — and because we **precompute**, Ollama runs on *your* machine during `run_today.py`, bakes the wording into `today.json`, and the public site just displays it (**local Ollama serves a public site fine — users never call it, and you can proofread the text before it ships**). Always wrap it: `try llm_summarize() except → template()`. Never let the LLM invent a number or break the demo.

---

## 8. The website (what's built) — `atlas/setscout/`

The **"shop window"** (webapp layer), fully working:

- **Files:** `setscout/index.html` (the whole app, ~1 file) · `setscout/today.json` (the data, the contract) · `setscout/gen_today.js` (Node script that generates the SET100 mock).
- **Live:** https://oksoimcodingnow.github.io/atlas/setscout/
- **Features:** SET100 list → tap a stock → the 4 sentences (bottom-sheet) · filter chips (✅🟡🔴) · **light/dark theme** · **TH/EN toggle** · **risk quiz → personalized ranking + position sizing** · disclaimer baked in · responsive (phone→iPad→desktop). All state saved in `localStorage`.
- **How it works:** `fetch('today.json')` → renders cards → templates the raw numbers into the 4 Thai/English sentences in-page (this IS the "translator, no LLM" pattern, live). The `because` reasons are stored as **language-neutral codes** (`"momentum:pos"`) and rendered TH/EN from a `REASON` map.
- ⚠️ **The numbers are MOCK.** Real SET100 *tickers*, but scores/risk are procedurally generated by `gen_today.js` (deterministic seed). **The real engine just overwrites `today.json` with the same shape — the website doesn't change.** That's the contract paying off.

### 🔒 The `today.json` contract (LOCKED — build the engine to this)
```json
{
  "generated": "2026-07-31", "universe": "SET100",
  "disclaimer": "…",
  "stocks": [{
    "ticker": "ADVANC.BK", "name": "Advanced Info Service", "name_th": "เอไอเอส",
    "sector": "ICT", "score": 0.81, "verdict": "BUY",         // BUY | WAIT | AVOID
    "risk_month_pct": -9,       // Monte-Carlo normal-bad month (%)
    "max_weight": 0.34,         // position-size cap (fraction of 100)
    "p_win": 0.61,              // calibrated hit-rate → trust label
    "because": ["quality:pos","momentum:pos"],   // factor:dir codes
    "last": 285.0, "chg_pct": 0.7
  }]
}
```
Field meanings: `score` 0–1 composite · `verdict` from thresholds · `risk_month_pct`/`max_weight` from the Monte-Carlo risk job · `p_win` from the ML job · `because` = the 2 strongest/weakest factors. **The translator (Python) will eventually produce the finished sentences too — but the shape above is what the webapp needs.**

---

## 9. What to lock / do next 🎯

1. **🎯 The ML label (do first):** define the target precisely — e.g. *"did the stock beat the SET index by >X% over the next N days?"* Lock horizon + threshold **before** modeling (pre-registration).
2. **Universe:** **SET100** (decided). Handle **delisted** names or the backtest lies (survivorship bias).
3. **Pre-registration** (`paper/pre-registration.md`): write rules, weights-source, metrics, holdout split *before* running.
4. **Connect the real engine:** produce a real `today.json` (same shape) → the website lights up automatically.
5. **Primary data:** put the survey into Google Forms (pilot on 5 first) · run the AHP with experts (Pim will share when the expert-risk data is in).
6. **🔓 Google auth — OPEN DECISION.** Wanted, but needs setup + a purpose. Recommended path (fits Pim's Firebase experience): **Firebase Authentication (Google provider)** on the static site → lets users **save their risk profile / watchlist across devices**. Needs: create a Firebase project (their Google account), add the config to `index.html`, authorize the Pages domain, and consider **PDPA** (you'd now hold Google identities). *Do it only if cross-device save matters; the localStorage version already personalizes without any login. Claude can scaffold it once the Firebase project exists.*

---

## 10. Glossary (quick)
**AHP** = Analytic Hierarchy Process (pairwise → weights + consistency check) · **walk-forward** = re-test across many time windows to avoid one lucky fit · **luck bar** = how good the *best of N random ideas* would look, so you can't fool yourself · **frozen/sealed holdout** = test data touched once at the very end · **max_weight** = position-size cap from Monte-Carlo risk · **verdict** = BUY/WAIT/AVOID · **secondary data** = markets (yfinance/SET) · **primary data** = humans (surveys/experts).

**References:** SET50/100 constituents — set.or.th · AHP — Saaty (1980) · factors — Fama-French (value/momentum/quality/low-vol) · financial-literacy Big Three — Lusardi & Mitchell · Thai PDPA · yfinance (unofficial Yahoo data).

---
*Golden rule for the junior: you may draft anything with AI, but you must be able to **explain every line you commit** — Q&A day is merciless. If you can't explain it, delete it.* 🧠
