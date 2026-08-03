# 😅 No idea what's going on? You're in the right place.

*Breathe. This folder exists so nobody feels lost. Here's the whole project in the simplest words.*
**ไม่รู้ว่านี่คืออะไร? ไม่เป็นไร เริ่มตรงนี้เลย — อธิบายแบบง่ายที่สุด**

---

## 🟢 What is this repo, in one line?

> **SETScout** — a website that finds **Thai stocks worth *researching*** and tells you the **risk**, honestly.

It's a school **Data Science** project. It does **NOT** tell you to buy anything. **Educational only, not investment advice.**

---

## 📂 What are all these folders? (decoded)

When you look at this repo you'll see a bunch of folders. Here's what each one *actually* is:

| You see this | It means… |
|---|---|
| 📁 **`app/`** | the **website** — the thing people actually look at (open `app/index.html`) |
| 📁 **`engine/`** | the **Python code** that scores the stocks + `today.json` (the data it makes) |
| 📁 **`docs/`** | **explanations** — the "how does this work" writing |
| 📁 **`research/`** | our **surveys** — the real data we collect from people (primary data) |
| 📁 **`proposals/`** | the original **plan & ideas** (how the project started) |
| 📄 **`README.md`** / **`START-HERE.md`** | the friendly front-door intros |

That's the *whole* repo. Nothing hidden. 🙂

---

## 🎯 Pick what you want to do

- 👀 **I just want to SEE it working**
  → Open the live demo: **https://oksoimcodingnow.github.io/atlas/setscout/**
  *(or open `app/index.html` in your browser)*

- 🧠 **I want to UNDERSTAND it**
  → Read **[`../START-HERE.md`](../START-HERE.md)** (5 minutes) → then **[`../docs/HOW-IT-WORKS.md`](../docs/HOW-IT-WORKS.md)** (the full, still-plain version).

- 💻 **I want to RUN it myself**
  → `pip install pandas numpy yfinance` → `cd engine` → `python run_today.py`

---

## 🧭 The 30-second mental model

```
  engine/  makes the data   →   today.json   →   app/  shows it to people
  (Python)                       (a file)          (website)
```
The code runs *ahead of time* and saves a file. The website just *reads* that file. That's the whole trick.

---

## ⭐ The one rule to remember

**SETScout points you to “research,” it never says “buy.”** Soft wording, disclaimers everywhere, non-commercial.

---

*Still stuck? Ask in the group — asking is not embarrassing, it's how teams work. 🙌*
*ยังงงอยู่? ถามในกลุ่มได้เลย การถามคือเรื่องปกติของการทำงานเป็นทีม*
