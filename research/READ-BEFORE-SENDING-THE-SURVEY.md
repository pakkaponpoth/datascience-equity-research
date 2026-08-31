# ⚠️ อ่านก่อนส่งแบบสอบถาม / Read before sending the survey

**เขียนเมื่อ 1 ก.ย. 2569 · ไม่ได้ลบหรือแก้ไฟล์เดิมของใคร**

มีไฟล์แบบสอบถามผู้เชี่ยวชาญ **สองฉบับ** ในโฟลเดอร์นี้ และมันถามคนละเรื่องกัน
ต้องเลือกก่อนส่ง ไม่งั้นเราจะได้ข้อมูลที่เอาไปใช้ไม่ได้

> There are now **two** expert questionnaires here and they ask about different
> things. Pick one before sending, or the responses will not be usable.

| ไฟล์ | ปัจจัย | นิยาม |
|---|---|---|
| `expert-ahp.md` (ของเดิม) | **6** ตัว รวม *Sentiment* | P/E, P/B, ROE, net margin, D/E — **ปัจจัยพื้นฐาน** |
| `expert-ahp-engine-aligned.md` (ใหม่) | **5** ตัว | ราคาล้วน ๆ — ตรงกับที่ engine คำนวณจริง |

---

## ปัญหา / The problem

`expert-ahp.md` เป็นแบบสอบถามที่เขียนได้ดี มีส่วนขอความยินยอมและตัวเลือกการอ้างอิงชื่อ
ที่ฉบับใหม่ยังไม่มี **แต่มันถามถึงปัจจัยที่ engine ไม่ได้คำนวณ**

The existing questionnaire is well written — its consent section and citation
options are better than the new one's. **But it asks about factors the engine
does not compute.**

| แบบสอบถามเดิมถามว่า | `run_today.py` คำนวณจริง |
|---|---|
| Value = P/E, P/B, dividend yield | ราคาเทียบค่าเฉลี่ย 200 วันของตัวเอง |
| Quality = ROE, net margin, low debt | ความผันผวน (annualised volatility) |
| Health = D/E, liquidity, earnings stability | ขาดทุนสูงสุด 1 ปี (max drawdown) |
| Growth = revenue & EPS growth | ผลตอบแทนราคา 12 เดือน |
| **Sentiment = news sentiment score** | **ไม่มีในระบบเลย** |

ถ้าส่งฉบับเดิมออกไป เราจะได้น้ำหนักที่ผู้เชี่ยวชาญให้กับ *P/E และ ROE*
แล้วเอาไปคูณกับ *ความผันผวนและ drawdown* ซึ่งเป็นคนละอย่างกัน
และจะมีน้ำหนักของ Sentiment ที่ไม่มีที่ให้ใส่

> Send the original and we collect expert weights for **P/E and ROE**, then apply
> them to **volatility and drawdown** — different quantities entirely. Plus a
> Sentiment weight with nowhere to go.

---

## ทางเลือก / Options

**A — ส่งฉบับใหม่ (`expert-ahp-engine-aligned.md`)**
ได้น้ำหนักที่ใช้ได้ทันทีกับ engine ปัจจุบัน แต่ยอมรับว่าเรากำลังถามเรื่อง
ปัจจัยที่มาจากราคาล้วน ๆ ซึ่งเป็นข้อจำกัดที่เรารายงานอยู่แล้ว
**ควรยกส่วน Consent และตัวเลือกอ้างอิงชื่อจากฉบับเดิมมาใส่** — ฉบับใหม่ยังไม่มี

**B — ส่งฉบับเดิม แล้วสร้าง v2 ของ engine ให้ตรง**
ได้ข้อมูลที่ดีกว่าในระยะยาว แต่ต้องเพิ่มปัจจัยพื้นฐาน (P/E, ROE) และ Sentiment
เข้า engine ก่อน ซึ่งเป็นงานใหญ่และ Protocol ระบุว่า **ยังไม่พร้อมทำ v2**

**C — ส่งทั้งสองฉบับให้คนละกลุ่ม**
ได้ทั้งน้ำหนักที่ใช้ได้ตอนนี้ และแผนที่สำหรับ v2 แต่ต้องใช้ผู้เชี่ยวชาญมากขึ้น
ซึ่งเรามีจำกัด (เป้าหมาย 6–10 คน)

**ข้อเสนอ: A** — เพราะ v2 ยังไม่พร้อม และน้ำหนักที่เอาไปใช้ไม่ได้ก็ไม่มีประโยชน์
โดยยก Consent จากฉบับเดิมมาใช้

---

## ไม่ว่าจะเลือกอะไร / Either way

`ahp_analyze.py` ในโฟลเดอร์นี้รองรับ **5 ปัจจัย** ตามฉบับใหม่
ถ้าเลือก B หรือ C ต้องแก้ `FACTORS` และ `RI[6] = 1.24` ในสคริปต์

ทดสอบ pipeline ได้เลยโดยไม่ต้องรอคำตอบจริง:

```bash
python research/ahp_analyze.py --demo
```

มันจะสร้างผู้เชี่ยวชาญปลอม 8 คน ตรวจ Consistency Ratio รวมน้ำหนัก
และรายงานช่วงความไม่เห็นตรงกัน — ซึ่งช่วงนั้นแหละที่จะกลายเป็นช่วงทดสอบ
sensitivity แทนที่จะมั่ว ±10% เอาเอง

> The analysis script expects the **5-factor** version. Choosing B or C means
> editing `FACTORS` and using `RI[6] = 1.24`. Run `--demo` to exercise the whole
> pipeline on synthetic experts before any real response arrives.
