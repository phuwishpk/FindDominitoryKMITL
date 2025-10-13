# 📘 Commands Used (Git/GitHub)

### รวมคำสั่ง Git/GitHub ที่ใช้ในโปรเจกต์นี้ เพื่อความสะดวกในการทำงานร่วมกัน

### 📌 เริ่มต้นใช้งาน (Setup)
```bash
# Step 1 : คลิกขวาที่หน้า Desktop เเล้วกด Open Git Bash here

# Step 2 : โคลน repo จาก GitHub ลง local (เครื่องคอมพิวเตอร์ของเรา)
git clone https://github.com/phuwishpk/FindDominitoryKMITL.git

# Step 3 : เปิดโปรเจกต์ด้วย VS Code
code FindDominitoryKMITL/

##### หลังจาก clone Repo ลงเครื่องเเล้ว เมื่อเปิด-ปิดคอม เเล้วจะมาทำงานใหม่ทำตามนี้ #####
# 1.คลิกขวาที่หน้า Desktop เเล้วกด Open Git Bash here
# 2.เปิดโปรเจกต์ด้วย VS Code
code FindDominitoryKMITL/
```

---
---
---
### 📌 การสร้าง Branch ใหม่สำหรับแต่ละคน
- **ทุกๆคนจะไปอยู่ที่ Branch main หลังจากเปิดโปรเจกต์ โดยที่เราจะเเตก Branch โดยใช้ Source จาก develop-project เเต่ต้องใช้คำสั่งนี้ก่อน เพื่อเป็นการย้าย Branch**
```bash
git switch develop-project
```
- **หลังจากย้ายมาจาก main สู่ develop-projetc ก็สร้าง branch ของเเต่ละคนจาก source ของ develop-project**
```bash
git checkout -b "ชื่อ Branch ที่ได้รับหมอบหมาย + ชื่อภาษาอังกฤษเเละเลข 3 ตัว"
# ตัวอย่าง : git checkout -b "owner-crud-gallery-o1-Tanabordi298"
```
- **หลังจากการสร้าง branch ใน local (เครื่องคอมพิวเตอร์ของเรา) เเล้วจะให้แสดงใน remote (Repo บน Github) ใช้คำสั่ง**
```bash
git push -u origin "ชื่อ Branch ตัวเอง"
# ตัวอย่าง : git push origin "owner-crud-gallery-o1-Tanabordi298"
# โดยเป็นการส่ง branch ไป และผูก local ↔ remote
```
### เป็นการจบการเเตก Branch เรียบร้อย


---
---
---
### 📌 การ Add & Commit & Push
```bash
# ตรวจสอบสถานะไฟล์ที่เปลี่ยนแปลง
git status

# การที่เราจะทำการ git add งานของเรา ก็จะต้อง cd ไปที่โฟลเดอร์ของงานนั้นๆ (เพื่อ Push งานเฉพาะเจาะจง)
cd "ชื่อโฟลเดอร์"

# หลังจากเข้าโฟล์เดอร์นั้นเเล้ว เจอชื่อไฟล์ใช้คำสั่ง
git add "ชื่อไฟล์"
# (Tips : เราสามารถไม่ต้องพิมชื่อไฟล์ทั้งหมด โดยเราสามารถพิมชื่อตัวเเรกของชื่อไฟล์ เเละกด tab มันจะระบุชื่อไฟล์มาให้เราเลย)

# commit พร้อมข้อความ
git commit -m "ข้อความ commit (เป็นการอธิบายว่าได้กระทำอะไรลงไปบ้างในไฟล์งานนั้น)"

# push ขึ้นไปยัง branch ของตัวเอง
git push
# จะใช้คำสั่ง git push ได้ก็จะต้องใช้คำสั่ง git push -u origin มาก่อนหน้าเเล้ว
```

---
---
---
### 📌 การดึงงานล่าสุดจาก Remote (git pull)
- **เพื่อให้ Branch ของเราทันสมัยกับ Remote ก่อนเริ่มทำงาน หรือก่อน Push**
```bash
git pull
```
- **กรณีต้องการดึงจาก branch อื่นแบบเจาะจง**
```bash
git pull origin "ชื่อ Branch"
# ตัวอย่าง: git pull origin develop-project
```
- **🔹 หมายเหตุ :**
ควรทำ git pull ก่อนเริ่มงานทุกครั้ง เพื่อหลีกเลี่ยง Conflict เเละ ถ้ามีการแก้ไขบน Remote Git จะรวมกับงานของเราโดยอัตโนมัติ

---

---
---
### 📌 การอัปเดต Local ให้ทันกับงานของคนอื่น
- **เมื่อคนอื่นทำงานใน branch ของตัวเอง และ push ขึ้น GitHub แล้ว เราต้องการให้ local ของเราทันสมัยเสมอ ใช้คำสั่งดังนี้**
```bash
# ดึงงานล่าสุดจาก branch อื่น (Remote → Local)
git fetch
```
- **คำสั่งนี้จะดึงข้อมูลล่าสุดจาก remote แต่ยังไม่ merge กับ branch ของเรา**
- **เหมาะสำหรับเช็กว่ามี branch หรือ commit ใหม่ ๆ บน remote**
---
---
---

### Branching Guide for Team Collaboration

คู่มือการแตก branch สำหรับการทำงานเป็นทีม

## 🌱 การสร้าง Branch ใหม่สำหรับแต่ละคน
**สร้าง branch ใหม่จาก develop-project**

```bash
git checkout -b "ชื่อ Branch ที่ได้รับหมอบหมาย + ชื่อภาษาอังกฤษเเละเลข 3 ตัว"
```

**หลังจากสร้าง Branch ของตัวเองใน Local (อุปกรณ์ตัวเอง) ก็ต้องอัปเดตให้ใน Github ขึ้น Branch ของตัวเองโดยใช้คำสั่ง**
```bash
git push -u origin "ชื่อ Branch"
```

