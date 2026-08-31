# แบบสอบถามผู้เชี่ยวชาญ — น้ำหนักปัจจัยคัดหุ้น (AHP)
# Expert Survey — Stock Factor Weights (AHP)

**โครงงานวิชา Data Science (01526125) · มหาวิทยาลัย**
**เวลาที่ใช้ ~15 นาที · Approximately 15 minutes**

---

## ทำไมเราถึงขอความเห็นคุณ / Why we are asking you

เราสร้างเครื่องมือคัดหุ้นไทยชื่อ **SETScout** ที่ให้คะแนนหุ้น SET100 จาก 5 ปัจจัย
ปัญหาคือ **น้ำหนักของแต่ละปัจจัยตอนนี้เราตั้งขึ้นเอง** ไม่มีหลักฐานรองรับ
เราจึงอยากได้ความเห็นจากผู้มีประสบการณ์จริง มาแทนที่ตัวเลขที่เราเดาเอง

> We built a Thai stock screener that scores SET100 stocks on five factors.
> **The factor weights are currently our own guesses with no evidence behind them.**
> This survey replaces them with judgements from people who actually know the market.

**ไม่มีคำตอบถูกหรือผิด** เราต้องการความเห็นเชิงวิชาชีพของคุณ ไม่ใช่คำตอบที่ "ควรจะเป็น"
และเราจะรายงานความ**ไม่**เห็นตรงกันระหว่างผู้ตอบด้วย เพราะนั่นคือข้อมูลสำคัญพอ ๆ กัน

---

## ปัจจัยทั้ง 5 / The five factors

อ่านให้ครบก่อนตอบ — คำนิยามของเราอาจไม่ตรงกับที่คุณคุ้นเคย

| ปัจจัย | เราวัดจาก | หมายเหตุสำคัญ |
|---|---|---|
| **โมเมนตัม** (Momentum) | ผลตอบแทน 6 เดือนที่ผ่านมา | ราคาล้วน ๆ |
| **การเติบโต** (Growth) | ผลตอบแทน 12 เดือนที่ผ่านมา | **เป็นการเติบโตของ*ราคา* ไม่ใช่ของกำไรบริษัท** |
| **ราคาเทียบค่าเฉลี่ย** (Value) | ราคาปัจจุบันเทียบค่าเฉลี่ย 200 วันของหุ้นตัวเอง | **ไม่ใช่ P/E** ไม่ได้เทียบกับกำไร |
| **คุณภาพ** (Quality) | ความผันผวนต่ำ (annualised volatility) | **ไม่ใช่คุณภาพกำไร** เป็นความนิ่งของราคา |
| **สุขภาพ** (Health) | ขาดทุนสูงสุดในรอบ 1 ปี (max drawdown) | **ไม่ใช่ฐานะการเงิน** เป็นความทนทานของราคา |

> All five are computed from **price data only** — no revenue, earnings or debt.
> Please judge them as defined above, not as the words might normally suggest.

---

## วิธีตอบ / How to answer

แต่ละข้อ เปรียบเทียบปัจจัย **2 ตัว** แล้วตอบ 2 อย่าง:

1. **ตัวไหนสำคัญกว่า** — หรือตอบว่า "เท่ากัน"
2. **สำคัญกว่ามากแค่ไหน** ตามมาตราส่วนนี้

| คะแนน | ความหมาย |
|---|---|
| **1** | สำคัญเท่ากัน / Equally important |
| **3** | สำคัญกว่าเล็กน้อย / Moderately more |
| **5** | สำคัญกว่าชัดเจน / Strongly more |
| **7** | สำคัญกว่ามาก / Very strongly more |
| **9** | สำคัญกว่าอย่างยิ่ง / Extremely more |
| 2, 4, 6, 8 | ค่ากลางระหว่างระดับข้างบน |

**ตัวอย่าง** ถ้าคุณคิดว่า *คุณภาพ* สำคัญกว่า *โมเมนตัม* อย่างชัดเจน
ให้ตอบว่า ตัวที่สำคัญกว่า = **คุณภาพ**, ระดับ = **5**

---

## ⚠️ ข้อควรระวัง — ความสอดคล้อง / A note on consistency

ระบบจะตรวจสอบว่าคำตอบของคุณ**ขัดแย้งกันเองหรือไม่** เช่น ถ้าคุณตอบว่า
A สำคัญกว่า B และ B สำคัญกว่า C แต่แล้วตอบว่า C สำคัญกว่า A — นั่นคือความขัดแย้ง

เราคำนวณค่า **Consistency Ratio (CR)** และจะใช้เฉพาะคำตอบที่ **CR < 0.10**
ถ้าคำตอบของคุณเกินเกณฑ์ เราจะติดต่อกลับเพื่อขอให้ทบทวน ไม่ใช่การตัดสินว่าผิด
เป็นเรื่องปกติมากในแบบสอบถามลักษณะนี้

> We compute a Consistency Ratio and use only responses below 0.10. If yours
> exceeds it we will ask you to revisit a few answers — this is routine, not a failure.
> **We will report how many responses were excluded**, because hiding that would
> misrepresent the strength of our result.

---

# ส่วนที่ 1 — สำหรับนักลงทุน "สายระมัดระวัง"
# Block 1 — for a CAUTIOUS beginner

> ลองนึกภาพ: **มือใหม่ อายุ 22 เพิ่งเริ่มทำงาน เงินก้อนแรก รับความเสี่ยงได้น้อย
> กลัวขาดทุนมากกว่าอยากได้กำไรเร็ว**
> *A 22-year-old beginner, first savings, low risk tolerance, more afraid of
> losing than eager to gain.*

สำหรับนักลงทุนแบบนี้ ปัจจัยไหนควรมีน้ำหนักมากกว่ากัน

| # | เปรียบเทียบ | ตัวไหนสำคัญกว่า | ระดับ (1–9) |
|---|---|---|---|
| 1.1 | โมเมนตัม ↔ การเติบโต | ____________ | ______ |
| 1.2 | โมเมนตัม ↔ ราคาเทียบค่าเฉลี่ย | ____________ | ______ |
| 1.3 | โมเมนตัม ↔ คุณภาพ | ____________ | ______ |
| 1.4 | โมเมนตัม ↔ สุขภาพ | ____________ | ______ |
| 1.5 | การเติบโต ↔ ราคาเทียบค่าเฉลี่ย | ____________ | ______ |
| 1.6 | การเติบโต ↔ คุณภาพ | ____________ | ______ |
| 1.7 | การเติบโต ↔ สุขภาพ | ____________ | ______ |
| 1.8 | ราคาเทียบค่าเฉลี่ย ↔ คุณภาพ | ____________ | ______ |
| 1.9 | ราคาเทียบค่าเฉลี่ย ↔ สุขภาพ | ____________ | ______ |
| 1.10 | คุณภาพ ↔ สุขภาพ | ____________ | ______ |

---

# ส่วนที่ 2 — สำหรับนักลงทุน "สายสมดุล"
# Block 2 — for a BALANCED investor

> ลองนึกภาพ: **มีประสบการณ์บ้าง ลงทุนระยะ 3–5 ปี รับความผันผวนได้พอสมควร
> อยากได้ทั้งการเติบโตและความปลอดภัย**
> *Some experience, a 3–5 year horizon, tolerates moderate swings, wants both
> growth and safety.*

| # | เปรียบเทียบ | ตัวไหนสำคัญกว่า | ระดับ (1–9) |
|---|---|---|---|
| 2.1 | โมเมนตัม ↔ การเติบโต | ____________ | ______ |
| 2.2 | โมเมนตัม ↔ ราคาเทียบค่าเฉลี่ย | ____________ | ______ |
| 2.3 | โมเมนตัม ↔ คุณภาพ | ____________ | ______ |
| 2.4 | โมเมนตัม ↔ สุขภาพ | ____________ | ______ |
| 2.5 | การเติบโต ↔ ราคาเทียบค่าเฉลี่ย | ____________ | ______ |
| 2.6 | การเติบโต ↔ คุณภาพ | ____________ | ______ |
| 2.7 | การเติบโต ↔ สุขภาพ | ____________ | ______ |
| 2.8 | ราคาเทียบค่าเฉลี่ย ↔ คุณภาพ | ____________ | ______ |
| 2.9 | ราคาเทียบค่าเฉลี่ย ↔ สุขภาพ | ____________ | ______ |
| 2.10 | คุณภาพ ↔ สุขภาพ | ____________ | ______ |

---

# ส่วนที่ 3 — สำหรับนักลงทุน "สายบุก"
# Block 3 — for an AGGRESSIVE investor

> ลองนึกภาพ: **มีประสบการณ์ รับความผันผวนสูงได้ ลงทุนระยะยาว 5 ปีขึ้นไป
> ยอมรับการขาดทุนหนักในบางช่วงเพื่อโอกาสเติบโตสูง**
> *Experienced, tolerates high volatility, 5+ year horizon, accepts deep
> drawdowns in exchange for growth potential.*

| # | เปรียบเทียบ | ตัวไหนสำคัญกว่า | ระดับ (1–9) |
|---|---|---|---|
| 3.1 | โมเมนตัม ↔ การเติบโต | ____________ | ______ |
| 3.2 | โมเมนตัม ↔ ราคาเทียบค่าเฉลี่ย | ____________ | ______ |
| 3.3 | โมเมนตัม ↔ คุณภาพ | ____________ | ______ |
| 3.4 | โมเมนตัม ↔ สุขภาพ | ____________ | ______ |
| 3.5 | การเติบโต ↔ ราคาเทียบค่าเฉลี่ย | ____________ | ______ |
| 3.6 | การเติบโต ↔ คุณภาพ | ____________ | ______ |
| 3.7 | การเติบโต ↔ สุขภาพ | ____________ | ______ |
| 3.8 | ราคาเทียบค่าเฉลี่ย ↔ คุณภาพ | ____________ | ______ |
| 3.9 | ราคาเทียบค่าเฉลี่ย ↔ สุขภาพ | ____________ | ______ |
| 3.10 | คุณภาพ ↔ สุขภาพ | ____________ | ______ |

---

## ข้อมูลผู้ตอบ / About you

*ไม่บังคับ และเราไม่เก็บชื่อหรืออีเมลถ้าคุณไม่ให้*

- ประสบการณ์ในตลาดทุน / Years of market experience: ______
- บทบาท / Role (เช่น นักวิเคราะห์, ผู้จัดการกองทุน, อาจารย์, นักลงทุนรายบุคคล): ______________
- ยินดีให้ติดต่อกลับหากคำตอบไม่สอดคล้อง? ☐ ใช่ ☐ ไม่

**ถ้าคุณมีเวลาจำกัด** ตอบเพียงส่วนใดส่วนหนึ่งก็มีประโยชน์
ระบบวิเคราะห์รองรับคำตอบที่ไม่ครบทุกส่วน

---

## ความเป็นส่วนตัว / Privacy (PDPA)

หากคุณให้ชื่อหรืออีเมล ถือเป็นข้อมูลส่วนบุคคลตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล
เราจะใช้เพื่อ **ติดต่อกลับเรื่องความสอดคล้องของคำตอบเท่านั้น** ไม่เผยแพร่
ไม่ส่งต่อ และจะลบหลังส่งรายงานโครงงาน คุณขอให้ลบเมื่อใดก็ได้

ผลที่เผยแพร่จะเป็น**ค่ารวมแบบไม่ระบุตัวตน** เท่านั้น

> If you give a name or email it is personal data under Thailand's PDPA. It is used
> **only** to follow up on consistency, never published or shared, and deleted after
> the project is submitted. Published results are aggregate and anonymous.

**ขอบคุณมากครับ / Thank you.**

---

<!--
FOR THE TEAM — how to process responses
========================================
1. Enter each response as rows in research/ahp_responses.csv, format:

   respondent,profile,left,right,winner,strength

   respondent : any stable id, e.g. E01
   profile    : conservative | balanced | aggressive
   left,right : the two factors as written in the table, in English
                (momentum, growth, value, quality, health)
   winner     : which one they picked - must equal left or right, or "equal"
   strength   : 1-9 (use 1 when winner is "equal")

   A template with one worked respondent is in ahp_responses_template.csv.

2. Run:  python research/ahp_analyze.py

   It computes each respondent's priority vector by the row geometric mean,
   checks the Consistency Ratio against RI=1.12 for n=5, drops anyone above
   0.10, aggregates the survivors by geometric mean of judgements (AIJ), and
   bootstraps the respondents to produce per-stock top-10 stability.

3. Report ALL of: how many responded, how many were dropped and why, the mean
   CR, the weight spread across respondents, and the bootstrap stability. The
   exclusions and the disagreement are findings, not embarrassments.
-->
