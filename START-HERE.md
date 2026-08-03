# 👋 Start Here — SETScout

**New to this project? Read this first. 5 minutes and you'll get it.**
*เพิ่งเข้ามา? อ่านอันนี้ก่อน ~5 นาทีเข้าใจภาพรวม*

---

## What is SETScout, in one breath

> **SETScout finds Thai stocks worth *researching* — and tells you the risk, honestly.**

It is **not** a robot that predicts prices or tells you to buy. Every day it looks at ~92 big Thai stocks (SET100),
scores them on a few simple factors, sorts them into **Worth a look 🟢 / Wait 🟡 / Not now 🔴**, and explains each
one in plain sentences *with the risk attached*. It's even honest enough to admit when it can't beat the market —
**that honesty is the whole point.**

It's a **Data Science class project → educational, NOT investment advice.**

---

## How it works (the 60-second picture)

```
  📥 COLLECT        ⚙️ SCORE          🎚️ 3 ENGINES        📄 today.json        🌐 WEBSITE
  daily prices  →   5 factors     →   safe / balanced  →  ranked lists    →   shows 4 plain
  for ~92 SET       per stock,        / bold (different    saved to a file     sentences per
  stocks (Yahoo)    fair by sector    weightings)          (precomputed)       stock; quiz picks
                                                                               your engine
```

- **The engine runs ahead of time** and writes a file (`today.json`). The website just *reads* that file — so it's
  instant, and you can build the website without the engine even running.
- **Three "engines"** = the same factors weighted three ways, one per risk appetite. The website's risk quiz picks
  which list you see.

---

## The 4 sentences a user sees (this is the whole product)

1. **Verdict** — Worth a look / Wait / Not now
2. **Risk in baht** — *"a normal-bad month ≈ −16%, so put at most ฿23 of every 100"*
3. **Because** — *"price is above its long average and hasn't just spiked"*
4. **Trust label** — *"we don't promise profit, we tell you the risk"*

---

## Run it yourself (2 commands)

```bash
pip install pandas numpy yfinance      # one time
python run_today.py                    # refresh the picks (writes today.json)
python backtest.py                     # the honesty check (luck bar + calibration)
```
Then open `index.html` in a browser to see the website.

---

## Where's everything (repo map)

| File / folder | What it is |
|---|---|
| `index.html` | 🌐 **the website** — the shop window users see |
| `run_today.py` | ⚙️ **the engine** — pulls prices, scores, writes `today.json` |
| `today.json` | 📄 the data the website reads (made by the engine) |
| `backtest.py` | 🧪 the honesty checks (does it beat the market? beat random?) |
| `calibration.json` | 📊 output of the backtest (real hit-rates by score) |
| `setscout-map.html` | 🗺️ a visual system map |
| `research/` | 📋 **primary data** — the investor survey + AHP expert survey |
| `proposals/` | 📝 how we got here (the original ideas + team workflow) |
| `docs/HOW-IT-WORKS.md` | 📖 **the detailed explanation** — read this next |
| `HANDOFF.md` / `CONTINUE.md` | full design + current state |

---

## The one rule to remember

**SETScout points you to “research,” it never says “buy.”** Soft wording, disclaimers everywhere, non-commercial.
In Thailand, paid public "buy this stock" advice is regulated — as an educational project with disclaimers, we're fine.

➡️ **Next:** open [`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md) for the full, detailed walk-through.
