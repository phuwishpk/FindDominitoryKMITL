# 🏠 FindDormitoryKMITL — ระบบค้นหา/ประกาศหอพัก

โครงงาน **"เว็บค้นหาหอพัก KMITL"** จัดทำขึ้นเพื่อช่วยเหลือให้นักศึกษาสามารถค้นหาหอพักบริเวณสถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง (KMITL) ได้อย่างสะดวก รวดเร็ว และตอบโจทย์ความต้องการ

---

## 🎯 วัตถุประสงค์

- **อำนวยความสะดวก** แก่นักศึกษาในการค้นหาหอพักรอบ KMITL อย่างง่ายดายและมีประสิทธิภาพ
- **นำเสนอข้อมูลสำคัญ** ของหอพัก เช่น ที่ตั้ง ราคา สิ่งอำนวยความสะดวก ค่ามัดจำ ระยะทางจากสถาบัน รวมถึงรูปภาพประกอบ
- **พัฒนาระบบค้นหา** และการกรองข้อมูลที่ยืดหยุ่น เช่น การค้นหาตามช่วงราคา ประเภทหอพัก (ชาย/หญิง/รวม) หรือสิ่งอำนวยความสะดวก
- **ลดเวลาและความยุ่งยาก** ในการตัดสินใจ รวมถึงช่วยให้นักศึกษาใหม่หรือผู้ปกครองไม่จำเป็นต้องสำรวจพื้นที่จริงมากนัก
- **ส่งเสริมการใช้เทคโนโลยีดิจิทัล** เพื่อยกระดับคุณภาพชีวิตของนักศึกษาให้ดียิ่งขึ้น

---

## 👥 คณะผู้จัดทำ

| ชื่อ-นามสกุล | รหัสนักศึกษา |
|-------------|-------------|
| นาย ภูวิชญ์ ประกอบจิตร | 67030183 |
| นาย กร แดงทอง | 67030268 |
| นาย ธนบดี บุญภมร | 67030298 |
| นาย พรพรม สุขใจมิตร | 67030323 |
| นางสาว ภิญญาพัชญ์ บานบัว | 67030334 |
| นาย อัฐวุฒิ บัวเรียน | 67030359 |
| นาย อิทธิพัทธิ์ สุทธินวล | 67030360 |

---

## 📋 ภาพรวมระบบ

**FindDormitoryKMITL** เป็นระบบค้นหา/ประกาศหอพัก โดยแยกบทบาทผู้ใช้งานเป็น **3 กลุ่ม**:

### 🔵 User (ผู้ใช้งานทั่วไป)
- เข้าดูประกาศที่ผ่านการอนุมัติ (approved) พร้อมฟิลเตอร์ค้นหา
- ฟิลเตอร์หลัก: ค้นหาข้อความ, ราคา, ประเภทห้อง, สิ่งอำนวยความสะดวก, สถานะห้อง, ใกล้พิกัด, เรียงลำดับ

### 🟢 Owner (เจ้าของหอพัก)
- สมัคร/ล็อกอินด้วยอีเมล + รหัสผ่าน (รองรับ remember me)
- จัดการประกาศ: ชื่อหอ, ประเภทห้อง, ช่องทางติดต่อ, ค่าใช้จ่าย, พิกัด, ลิงก์, สถานะห้อง
- แกลเลอรีรูป: อัปโหลด/ลบ/ลากเรียง (สูงสุด 6 รูป, jpg/jpeg/png/webp, ≤ 3MB/รูป)

### 🔴 Admin (ผู้ดูแลระบบ)
- ล็อกอินด้วย username + รหัสผ่าน
- จัดการคิวอนุมัติ, เปลี่ยน workflow, บันทึก AuditLog

---

## 🛠️ เทคโนโลยีที่ใช้

##Framework หลักและส่วนขยาย (Framework and Extensions):
- ** Flask: 3.0.3
- ** Flask-SQLAlchemy: 3.1.1 (ใช้สำหรับจัดการฐานข้อมูล)
- ** Flask-Migrate (Alembic): 4.0.7 (ใช้สำหรับจัดการการเปลี่ยนแปลงโครงสร้างฐานข้อมูล)
- ** Flask-WTF + WTForms: 1.2.1 (ใช้สำหรับสร้างและจัดการฟอร์ม)
- ** Flask-Login: 0.6.3 (ใช้สำหรับจัดการการล็อกอินของผู้ใช้)
- ** Flask-Babel: 4.0.0 (ใช้สำหรับจัดการเรื่องภาษาและโซนเวลา)
- ** Flask-Limiter: 3.5.0 (ใช้สำหรับจำกัดจำนวนการร้องขอเพื่อป้องกันการโจมตี)
- ** Werkzeug: 3.0.3 (เป็นส่วนประกอบหลักของ Flask)
##ฐานข้อมูล (Database):
- ** SQLAlchemy: 2.0.29
- ** Alembic: 1.13.2
- ** psycopg2-binary: 2.9.9 (สำหรับเชื่อมต่อกับฐานข้อมูล PostgreSQL)
##เซิร์ฟเวอร์ (WSGI Server):
- ** gunicorn: 22.0.0 (สำหรับใช้งานบน production)
##เครื่องมืออื่นๆ (Other Tools):
- ** Bootstrap 5 (CDN)
- ** Jinja2: 3.1.4 (Template engine ของ Flask)
- ** python-dotenv: 1.0.1 (สำหรับจัดการ environment variables)
---

## 📁 โครงสร้างโปรเจค

```
FindDormitoryKMITL/
├─ run.py                          # Entry Point
├─ requirements.txt                # Dependencies
├─ instance/                       # Instance Config
├─ uploads/                        # Uploaded Files
└─ app/
   ├─ __init__.py                  # App Factory + DI Container
   ├─ config.py                    # Configuration
   ├─ extensions.py                # Flask Extensions
   │
   ├─ blueprints/
   │  ├─ public/routes.py          # User Routes (Search/Detail)
   │  ├─ owner/routes.py           # Owner Dashboard & CRUD
   │  ├─ admin/routes.py           # Admin Approval Queue
   │  ├─ auth/routes.py            # Login/Register/Logout
   │  └─ api/routes.py             # API Endpoints
   │
   ├─ models/
   │  ├─ user.py                   # User/Admin Models
   │  ├─ property.py               # Property/Image/Amenity
   │  └─ approval.py               # ApprovalRequest/AuditLog
   │
   ├─ repositories/
   │  ├─ interfaces/               # Repository Interfaces
   │  └─ sqlalchemy/               # SQLAlchemy Implementation
   │
   ├─ services/
   │  ├─ auth_service.py           # Authentication Logic
   │  ├─ property_service.py       # Property Management
   │  ├─ search_service.py         # Search & Filter
   │  ├─ approval_service.py       # Approval Workflow
   │  ├─ upload_service.py         # File Upload Handler
   │  └─ policies/                 # Business Policies
   │
   ├─ forms/
   │  ├─ auth.py                   # Auth Forms
   │  ├─ owner.py                  # Property Forms
   │  └─ upload.py                 # Upload Forms
   │
   ├─ utils/
   │  └─ validation.py             # Validation Helpers
   │
   └─ templates/
      ├─ base.html                 # Base Template
      ├─ public/                   # User Templates
      ├─ owner/                    # Owner Templates
      ├─ admin/                    # Admin Templates
      └─ auth/                     # Auth Templates
```

---

## 🚀 การติดตั้งและรัน

### ✅ ข้อกำหนดเบื้องต้น
- Python 3.11 หรือ 3.12
- pip (Python Package Manager)

### 📦 ขั้นตอนการติดตั้ง

```bash
# 1. ติดตั้ง Dependencies
pip install -r requirements.txt

# 2. สร้างตารางฐานข้อมูล (ครั้งแรก)
flask --app run.py db init
flask --app run.py db migrate -m "init schema"
flask --app run.py db upgrade

# 3. Seed ข้อมูลเริ่มต้น
flask --app run.py seed_amenities
flask --app run.py seed_sample
```

### ▶️ รันแอปพลิเคชัน

```bash
# วิธีที่ 1
python run.py

# วิธีที่ 2
flask run

# เปิดเบราว์เซอร์ที่
# http://127.0.0.1:5000/
```

### 🔧 แก้ไขปัญหา Database Error

```bash
# ถ้า run error เพราะ database ใช้คำสั่งนี้
flask --app run.py db upgrade
```

---

## 🔐 บัญชีทดสอบ

| บทบาท | Username/Email | Password |
|--------|----------------|----------|
| **Admin** | `admin` | `admin` |
| **Owner** | `owner@example.com` | `password` |

---

## 🎨 สถาปัตยกรรมระบบ

### Layered Architecture

```
┌─────────────────────────────────────┐
│   Presentation Layer                │
│   (Blueprints + Templates)          │
├─────────────────────────────────────┤
│   Service Layer                     │
│   (Business Logic)                  │
├─────────────────────────────────────┤
│   Repository Layer                  │
│   (Data Access)                     │
├─────────────────────────────────────┤
│   Model Layer                       │
│   (ORM Entities)                    │
└─────────────────────────────────────┘
```

---

## 👨‍💻 การแบ่งงานทีม (7 คน)

### 🔵 U1 - User Search/List (หนัก)
**ผู้รับผิดชอบ**: ฝั่ง User (ค้นหา/ลิสต์)

**ฟังก์ชันที่ต้องเขียน**:
- `SearchService.search_properties()` - ตรรกะค้นหาและกรองข้อมูล
- `SqlPropertyRepo.list_approved_with_filters()` - Query ฐานข้อมูลพร้อมฟิลเตอร์
- `public.routes.index()` - หน้าแสดงรายการหอพัก
- `public.routes.property_detail()` - หน้ารายละเอียดหอพัก

**Branch**: `feat/user-search-u1`

---

### 🔵 U2 - Review System
**ผู้รับผิดชอบ**: ระบบรีวิว (การคอมเมนต์และให้คะแนน)

**ฟังก์ชันที่ต้องเขียน**:
- `ReviewService.add_review()` - เพิ่มรีวิว
- `ReviewService.get_reviews_and_average_rating()` - ดึงรีวิวและคำนวณคะแนนเฉลี่ย
- `ReviewRepoSql.add()` - บันทึกรีวิวลงฐานข้อมูล
- `ReviewRepoSql.get_by_property_id()` - ดึงรีวิวของหอพัก
- `utils.validation.is_valid_citizen_id()` - ตรวจสอบบัตรประชาชน

**Branch**: `feat/user-review-system-u2`

---

### 🔵 U3 - History Tracking
**ผู้รับผิดชอบ**: ระบบประวัติการเข้าชม

**ฟังก์ชันที่ต้องเขียน**:
- `HistoryService.add_viewed_property()` - บันทึกหอพักที่เข้าชม
- `HistoryService.get_viewed_properties()` - ดึงประวัติการเข้าชม
- `public.routes.history()` - หน้าประวัติ
- `api.routes.api_health()` - Health Check Endpoint
- ปรับ `templates/base.html` + pagination helpers

**Branch**: `feat/user-history-tracking-u3`

---

### 🟢 O1 - Owner CRUD + Gallery (หนัก)
**ผู้รับผิดชอบ**: Owner Dashboard และจัดการประกาศ

**ฟังก์ชันที่ต้องเขียน**:
- `PropertyService.create_property()` - สร้างประกาศใหม่
- `PropertyService.update_property()` - แก้ไขประกาศ
- `UploadService.save_property_image()` - บันทึกรูปภาพ
- `owner.routes.dashboard()` - หน้าแดชบอร์ด
- `owner.routes.new_property()` - หน้าสร้างประกาศ
- `owner.routes.edit_property()` - หน้าแก้ไขประกาศ
- `owner.routes.upload_property_image()` - อัปโหลดรูป
- `owner.routes.delete_property_image()` - ลบรูป
- `owner.routes.reorder_property_images()` - เรียงลำดับรูป

**Branch**: `feat/owner-crud-gallery-o1`

---

### 🟢 O2 - Owner Form & Amenities
**ผู้รับผิดชอบ**: ฟอร์มและสิ่งอำนวยความสะดวก

**ฟังก์ชันที่ต้องเขียน**:
- `PropertyForm.validate_room_type()` - ตรวจสอบประเภทห้อง
- `PropertyPolicy.can_upload_more()` - นโยบายจำกัดจำนวนรูป
- `PropertyService.update_property_amenities()` - อัปเดต amenities (M2M)

**Branch**: `feat/owner-form-amenities-o2`

---

### 🔴 A1 - Admin Approval Workflow (หนัก)
**ผู้รับผิดชอบ**: ระบบอนุมัติประกาศ

**ฟังก์ชันที่ต้องเขียน**:
- `ApprovalService.submit_property()` - ส่งคำขออนุมัติ
- `ApprovalService.approve_property()` - อนุมัติประกาศ
- `ApprovalService.reject_property()` - ปฏิเสธประกาศ
- `ApprovalService.get_audit_logs()` - ดึงบันทึกกิจกรรม
- `admin.routes.queue()` - หน้าคิวอนุมัติ
- `admin.routes.approve()` - อนุมัติ
- `admin.routes.reject()` - ปฏิเสธ
- `admin.routes.logs()` - หน้าบันทึกกิจกรรม
- `AuditLog.log()` - บันทึกกิจกรรม

**Branch**: `feat/admin-approval-workflow-a1`

---

### 🔴 A2 - Auth/Security/DI/Seeds
**ผู้รับผิดชอบ**: Authentication และระบบรักษาความปลอดภัย

**ฟังก์ชันที่ต้องเขียน**:
- `AuthService.register_owner()` - สมัครสมาชิก Owner
- `AuthService.verify_owner()` - ตรวจสอบรหัสผ่าน Owner
- `AuthService.login_owner()` - Login Owner
- `AuthService.verify_admin()` - ตรวจสอบรหัสผ่าน Admin
- `AuthService.login_admin()` - Login Admin
- `AuthService.logout()` - Logout
- `extensions.load_user()` - โหลด User จาก Session
- `extensions.owner_required()` - Decorator สำหรับ Owner
- `extensions.admin_required()` - Decorator สำหรับ Admin
- `auth.routes.login()` - หน้า Login
- `auth.routes.owner_register()` - หน้าสมัครสมาชิก
- `auth.routes.logout()` - Logout Route
- `__init__.register_dependencies()` - DI Container
- CLI Commands: `seed_amenities()`, `seed_sample()`

**Branch**: `feat/admin-auth-security-a2`

---

## 📝 Validation Rules

### 🆔 บัตรประชาชน
- **รูปแบบ**: 13 หลัก (พร้อม checksum validation)
- **ฟังก์ชัน**: `is_valid_citizen_id()`

### 📄 เอกสาร PDF
- **นามสกุล**: `.pdf`
- **ขนาดสูงสุด**: 10 MB
- **ฟังก์ชัน**: `validate_pdf_file()`

### 🖼️ รูปภาพ
- **นามสกุลที่อนุญาต**: `.jpg`, `.jpeg`, `.png`, `.webp`
- **ขนาดสูงสุด**: 3 MB ต่อรูป
- **จำนวนสูงสุด**: 6 รูปต่อประกาศ
- **ฟังก์ชัน**: `validate_image_file()`

---

## 🌿 Git Workflow

### การตั้งชื่อ Branch

```
<type>/<area>-<scope>-<owner>
```

**ตัวอย่าง**:
- `feat/user-search-u1`
- `feat/owner-crud-gallery-o1`
- `feat/admin-approval-workflow-a1`
- `fix/owner-upload-image-o1`
- `refactor/search-service-u1`

### การตั้งชื่อ Commit

```
<type>(<scope>): <description>
```

**ตัวอย่าง**:
- `feat(search): add amenities AND-filter + pagination`
- `fix(upload): handle large image files correctly`
- `refactor(auth): simplify login logic`

### การตั้งชื่อ Pull Request

```
<type>(<scope>): <description> (<owner>)
```

**ตัวอย่าง**:
- `feat(search): add filters & approved listing (U1)`
- `feat(owner): implement gallery drag & drop (O1)`

---

## 🔍 การค้นหาและฟิลเตอร์

### ฟิลเตอร์ที่รองรับ

| ฟิลเตอร์ | พารามิเตอร์ | ตัวอย่าง |
|---------|-----------|---------|
| **ค้นหาข้อความ** | `q` | `?q=หอพักใกล้มหาวิทยาลัย` |
| **ราคาต่ำสุด** | `min` | `?min=3000` |
| **ราคาสูงสุด** | `max` | `?max=5000` |
| **ประเภทห้อง** | `room_type` | `?room_type=studio` |
| **สถานะห้อง** | `availability` | `?availability=available` |
| **สิ่งอำนวยความสะดวก** | `amenities` | `?amenities=wifi,parking` |
| **เรียงลำดับ** | `sort` | `?sort=price_asc` |

---

## 🐛 Troubleshooting

### ❌ Error: No such command 'db'
**สาเหตุ**: Flask import app ไม่ผ่าน

**แก้ไข**: ตรวจสอบ traceback ด้านบนสุดและแก้ไข import

---

### ❌ ModuleNotFoundError: app.forms.auth
**สาเหตุ**: ไฟล์ไม่ถูกสร้าง

**แก้ไข**: 
```bash
# สร้างไฟล์
touch app/forms/auth.py
touch app/forms/__init__.py
```

---

### ❌ ValueError: blueprint name 'auth' is already registered
**สาเหตุ**: Register blueprint ซ้ำ

**แก้ไข**: ตรวจสอบ `create_app()` ว่ามีการ register ซ้ำหรือไม่

---

### ❌ IndentationError
**สาเหตุ**: ไฟล์เยื้องบรรทัดผิด

**แก้ไข**: ใช้ editor ที่แสดง whitespace และตรวจสอบการเยื้อง

---

### ❌ อัปโหลดรูปไม่สำเร็จ
**สาเหตุ**: ปัญหาชนิด/ขนาดไฟล์ หรือสิทธิ์เขียนไฟล์

**แก้ไข**:
- ตรวจสอบชนิดไฟล์ (jpg/jpeg/png/webp)
- ตรวจสอบขนาดไฟล์ (≤ 3MB)
- ตรวจสอบสิทธิ์ `UPLOAD_FOLDER`

---

## 📚 แนวทางพัฒนาต่อยอด

### 🎯 Features ที่แนะนำ
- 🔔 ระบบแจ้งเตือน (Notifications)
- ⭐ ระบบรีวิวและให้คะแนน
- 📊 Dashboard สถิติสำหรับ Owner
- 🗺️ แผนที่แสดงตำแหน่งหอพัก (Google Maps API)
- 💬 ระบบแชทระหว่าง Owner และ User
- 📱 Responsive Design สำหรับมือถือ
- 🔒 Two-Factor Authentication (2FA)
- 📧 Email Verification

---
