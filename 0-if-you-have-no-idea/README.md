# 😅 No idea what's going on? You're in the right place.

*Breathe. This folder exists so nobody feels lost. Here's the whole project in the simplest words.*
**ใจเย็น ๆ ก่อน โฟลเดอร์นี้มีไว้เพื่อไม่ให้ใครรู้สึกตามไม่ทัน — อธิบายทั้งโปรเจกต์แบบง่ายที่สุด**

---

## 🟢 What is this, in one line? · นี่คืออะไร (บรรทัดเดียว)

> **SETScout** — a website that finds **Thai stocks worth *researching***, and tells you the **risk** honestly.
> **เว็บที่ช่วยหาหุ้นไทยที่ "น่าไปศึกษาต่อ" พร้อมบอกความเสี่ยงตามจริง**

It's a school **Data Science** project. It does **NOT** tell you to buy anything.
เป็นโปรเจกต์วิชา Data Science **ไม่ได้บอกให้ซื้ออะไรทั้งนั้น** — เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำการลงทุน

---

## 🔍 The most important part: what we actually found
## สิ่งที่สำคัญที่สุด: เราค้นพบอะไรบ้าง

*This is the real work. Not the website — these four things.*
*นี่คือเนื้องานจริง ไม่ใช่ตัวเว็บ แต่คือ 4 ข้อนี้*

### 1. We caught our own website telling a lie 🚨
It showed **"Hit rate 66%"** — as if the top stocks went up 66% of the time.
That number was never measured. A formula invented it: `0.44 + 0.22 × score`.

When we actually measured it, every group of stocks went up about **47%** of the time —
and the *highest-scoring* group did **no better** than the lowest.

**เว็บเราเคยขึ้นว่า "โอกาสเข้าทาง 66%" ทั้งที่ไม่เคยวัดจริง** เป็นแค่สูตรที่เราแต่งขึ้นเอง
พอวัดจริง ทุกกลุ่มขึ้นประมาณ **47%** เท่ากันหมด และกลุ่มคะแนนสูงสุดก็ **ไม่ได้ดีกว่า** กลุ่มคะแนนต่ำสุดเลย

✅ Fixed. The site now shows the measured number and says the score can't predict direction.
✅ แก้แล้ว ตอนนี้เว็บแสดงตัวเลขที่วัดจริง และบอกตรง ๆ ว่าคะแนนทำนายทิศทางไม่ได้

### 2. Two of our original five "different" measurements were the same thing 🔁
We used to score stocks on 5 things. Two of them — **"Value"** (cheap compared to its own average)
and **"Momentum"** (went up recently) — turned out to be **the same number with a minus sign**.
Correlation **−0.93**. A stock is "cheap" *because* it hasn't gone up.

**เดิมเรามี 5 ปัจจัย แต่ 2 ตัวคือตัวเดียวกันแค่กลับเครื่องหมาย** ค่าสหสัมพันธ์ **−0.93**
หุ้น "ถูก" ก็เพราะมันยังไม่ขึ้น นั่นแหละ

That broke the **"Balanced"** option — the one most people get from the quiz.
It was giving almost the same stocks as **"Conservative"** (8 out of 10 identical).

ทำให้โปรไฟล์ **"สมดุล"** เสีย — ได้หุ้นเกือบเหมือน **"ปลอดภัย"** (ซ้ำกัน 8 จาก 10 ตัว)

✅ Fixed. We deleted the duplicate, so SETScout now uses **4 factors**. Balanced has its own picks
instead of copying Conservative — though it still leans a little cautious.
✅ แก้แล้ว ลบตัวซ้ำออก ตอนนี้เหลือ **4 ปัจจัย** และโปรไฟล์สมดุลมีหุ้นของตัวเองแล้ว (แม้ยังเอียงไปทางปลอดภัยอยู่บ้าง)

### 3. Our picks do **not** beat just buying everything 📉
We tested it many different ways — holding 6 months, 12 months, rebalancing every
15 days, every month, every year. **None of them won.**

**เราทดสอบหลายแบบมาก ไม่มีแบบไหนชนะการซื้อทั้งตลาดแล้วถือไว้เฉย ๆ เลย**

**This is not a failure — it IS the project.** Most simple rules lose to just buying and
holding. Almost nobody proves that honestly. We did, and we say it on the website.

**นี่ไม่ใช่ความล้มเหลว แต่คือตัวโปรเจกต์เลย** กฎง่าย ๆ ส่วนใหญ่แพ้การถือยาว
แทบไม่มีใครกล้าพิสูจน์เรื่องนี้อย่างตรงไปตรงมา แต่เราทำ และเขียนไว้บนเว็บด้วย

### 4. We keep making the same mistake 🔧
Four times now, we wrote something down in one place and **forgot to connect it** to the
place that uses it. The measured hit-rate sat in a file for months, unused. The factor
list got copy-pasted into ten files and they drifted apart.

**เราทำผิดแบบเดิมซ้ำ 4 ครั้ง** คือเขียนอะไรไว้ที่หนึ่ง แล้วลืมต่อสายไปยังที่ที่ใช้จริง

**Noticing our own repeated mistake is worth more than any single bug fix.**
**การที่เรามองเห็นว่าตัวเองพลาดแบบเดิมซ้ำ ๆ มีค่ามากกว่าการแก้บั๊กทีละตัว**

> 💡 **New rule / กฎใหม่:** before adding anything, ask — *does this already exist somewhere else?*
> ก่อนจะเพิ่มอะไร ถามก่อนว่า *สิ่งนี้มีอยู่ที่อื่นแล้วหรือเปล่า?*

---

## 📂 What are all these folders? · โฟลเดอร์พวกนี้คืออะไร

| You see this | It means… · แปลว่า |
|---|---|
| 📁 **`app/`** | the **website** — what people look at · **ตัวเว็บ** ที่คนเห็น (`app/index.html`) |
| 📁 **`engine/`** | the **Python code** that scores stocks + `today.json` · **โค้ดที่ให้คะแนนหุ้น** และไฟล์ข้อมูล |
| 📁 **`docs/`** | **explanations** — the "how it works" writing · **คำอธิบาย** ว่าระบบทำงานยังไง |
| 📁 **`research/`** | our **surveys** — real data we collect from people · **แบบสอบถาม** ข้อมูลปฐมภูมิที่เราเก็บเอง |
| 📁 **`reports/`** | **test results**, saved automatically · **ผลการทดสอบ** ที่บันทึกอัตโนมัติ |
| 📁 **`proposals/`** | the original **plan** · **แผนตอนเริ่มโปรเจกต์** |

That's the whole repo. Nothing hidden. 🙂 · ทั้งหมดมีเท่านี้ ไม่มีอะไรซ่อน

**One file to know:** `engine/factors.py` holds the factor definitions. Everything imports
from it. Don't copy those numbers anywhere — that's mistake #4 above.
**ไฟล์ที่ควรรู้:** `engine/factors.py` เก็บนิยามปัจจัยไว้ที่เดียว **อย่าก๊อปตัวเลขไปไว้ที่อื่น**

---

## 🎯 Pick what you want to do · เลือกสิ่งที่อยากทำ

- 👀 **Just SEE it working** · แค่อยากดูว่ามันทำงานยังไง
  → **https://setscout-th.web.app**

- 🧠 **UNDERSTAND it** · อยากเข้าใจ
  → [`../START-HERE.md`](../START-HERE.md) (5 min) → [`../docs/HOW-IT-WORKS.md`](../docs/HOW-IT-WORKS.md)

- 💻 **RUN it yourself** · อยากลองรันเอง
  → `pip install pandas numpy yfinance` → `cd engine` → `python run_today.py`

---

## 🧭 The 30-second mental model · ภาพรวมใน 30 วินาที

```
  engine/  makes the data   →   today.json   →   app/  shows it
  (Python)                       (one file)        (website)
```

The code runs **ahead of time**, once a day, and saves a file. The website just **reads**
that file. Nobody waits for anything to calculate. That's the whole trick.

โค้ดรัน **ล่วงหน้า** วันละครั้ง แล้วเซฟเป็นไฟล์ เว็บแค่ **อ่านไฟล์** ผู้ใช้ไม่ต้องรอคำนวณ

---

## ⭐ The one rule · กฎข้อเดียวที่ต้องจำ

**SETScout points you to "research," it never says "buy."**
**SETScout บอกว่า "ไปศึกษาต่อ" ไม่เคยบอกว่า "ซื้อ"**

Soft wording, disclaimers everywhere, non-commercial. And if a number isn't measured,
we don't show it — we learned that one the hard way. 👆 (see finding #1)

---

*Still stuck? Ask in the group — asking is not embarrassing, it's how teams work. 🙌*
*ยังงงอยู่? ถามในกลุ่มได้เลย การถามไม่ใช่เรื่องน่าอาย มันคือวิธีทำงานเป็นทีม*
