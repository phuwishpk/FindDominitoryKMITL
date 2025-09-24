# 📘 Commands Used (Git/GitHub)

### รวมคำสั่ง Git/GitHub ที่ใช้ในโปรเจกต์นี้ เพื่อความสะดวกในการทำงานร่วมกัน

## 🔹 เริ่มต้นใช้งาน (Setup)
```bash
# ไปที่โฟลเดอร์ที่ต้องการเก็บโปรเจกต์
cd Desktop/

# โคลน repo จาก GitHub
git clone https://github.com/phuwishpk/FindDominitoryKMITL.git

# เปิดโปรเจกต์ด้วย VS Code
code FindDominitoryKMITL/
```
## 🔹 การ Commit & Push
```bash
# ตรวจสอบสถานะไฟล์ที่เปลี่ยนแปลง
git status

# เพิ่มไฟล์ทั้งหมดเข้าสู่ staging area
git add .

# หรือเพิ่มไฟล์เฉพาะเจาะจง โดยสามารถพิมคำเเรกของชื่อไฟล์เเละกด Tab จะได้ชื่อไฟล์ทั้นที
git add ชื่อไฟล์

# commit พร้อมข้อความ
git commit -m "ข้อความ commit"

# push ขึ้นไปยัง branch ที่ใช้งานอยู่ (เช่น main, dev)
git push origin <branch>
```
> ### 📝 หมายเหตุ  
> ### - ✅ ถ้าเคยใช้คำสั่ง  
>   ```bash
>   git push origin <branch>
>   ```  
>   ### ไปแล้ว รอบต่อไปสามารถใช้เพียง  
>   ```bash
>   git push
>   ```  
>   ### ได้เลย โดย Git จะจำ branch ที่เชื่อมไว้ให้อัตโนมัติ

>
> ### - ⚠️ แต่ถ้ายังไม่เคย push branch นั้นมาก่อน ต้องใช้  
>   ```bash
>   git push origin <branch>
>   ```  
>   ### ก่อนเสมอ

---
### Branching Guide for Team Collaboration

คู่มือการแตก branch สำหรับการทำงานเป็นทีม

## 🌱 การสร้าง Branch ใหม่สำหรับแต่ละคน
1. อัปเดต branch หลัก (`main`) ก่อนเริ่ม
```bash
git checkout main
git pull origin main
```
สร้าง branch ใหม่จาก main

```bash
git checkout -b feature/ชื่อคน-งาน
```