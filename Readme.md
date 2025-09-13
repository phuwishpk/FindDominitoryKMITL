# FindDormitoryKMITL — README

ระบบค้นหา/ประกาศหอพัก แยกบทบาท **User / Owner / Admin**  
เทคโนโลยี: **Flask**, **SQLAlchemy**, **Flask-Migrate**, **WTForms**, **Flask-Login**, **Bootstrap**

- หน้าเริ่มต้น: **User** (`/`) แสดงรายการประกาศที่อนุมัติแล้ว
- Navbar: ปุ่ม **Login** → หน้า Login รวม (เลือก Owner / Admin)
- Owner: สมัคร/ล็อกอิน, สร้าง/แก้ประกาศ, อัปโหลด/ลบ/ลากเรียงรูป (≤ 6 รูป)
- Admin: ล็อกอิน, (โครงพร้อมต่อยอด) อนุมัติ/ปฏิเสธ, บันทึก AuditLog

---

## ทีม/บทบาท (7 คน)

- **U1 (หนัก)** = ผู้รับผิดชอบฝั่ง User (ค้นหา/ลิสต์)
- **U2** = User-Map/Detail
- **U3** = User-UI
- **O1 (หนัก)** = Owner-CRUD/Gallery
- **O2** = Owner-Form/Amenities
- **A1 (หนัก)** = Admin-Approval Workflow
- **A2** = Admin-Auth/Security

> คน “หนัก” ทำ ≥ 3 ฟังก์ชัน; คนทั่วไปทำ ≥ 1 ฟังก์ชัน (แนะนำ 2)

---

## Folder Structure + ผู้รับผิดชอบ + ฟังก์ชันที่ “ต้องเขียน”

```bash

FindDormitoryKMITL/
├─ run.py — (A2) บูตแอป/entrypoint (ไม่ต้องแก้เยอะ)
├─ requirements.txt — (A2) ดูแล lib เพิ่มเติมเวลาใช้
├─ instance/
├─ uploads/
└─ app/
├─ init.py — (A2) DI container + register blueprints + CLI seed
│ • A2: ฟังก์ชันต้องเขียน/ดูแล
│ - register_dependencies(app): dict[str,Any] -> None (wire service/repo)
│ - seed_amenities(): None (CLI)
│ - seed_sample(): None (CLI)
├─ config.py — (A2) คอนฟิก (DB/UPLOAD/Locale)
├─ extensions.py — (A2) login_manager/db/migrate/csrf/limiter + decorators
│ • A2: ฟังก์ชันต้องเขียน/ดูแล
│ - load_user(user_id:str) -> Principal|None
│ - owner_required(f), admin_required(f) -> wrapper
│
├─ blueprints/
│ ├─ public/
│ │ └─ routes.py — (U1 — หนัก) หน้า User
│ │ • U1: ฟังก์ชันต้องเขียน
│ │ - index(): Response → รับ query-string → ส่งต่อ SearchService.search()
│ │ - property_detail(prop_id:int): Response
│ │ • U3 (เสริม): เพิ่ม pagination helper ถ้าต้อง
│ ├─ owner/
│ │ └─ routes.py — (O1 — หนัก) หน้า Owner CRUD + แกลเลอรี
│ │ • O1: ฟังก์ชันต้องเขียน
│ │ - dashboard(): Response
│ │ - new_property(): Response
│ │ - edit_property(prop_id:int): Response
│ │ - upload_image(prop_id:int): Response
│ │ - delete_image(prop_id:int, image_id:int): Response
│ │ - reorder_images(prop_id:int): Response
│ │ • O2 (เสริม): hook amenities ใน edit/new (ดู services/repo)
│ ├─ admin/
│ │ └─ routes.py — (A1 — หนัก) หน้า Admin queue + workflow
│ │ • A1: ฟังก์ชันต้องเขียน (แนะนำเพิ่ม)
│ │ - queue(): Response
│ │ - approve(prop_id:int): Response
│ │ - reject(prop_id:int): Response
│ │ - logs(page:int=1): Response
│ ├─ auth/
│ │ └─ routes.py — (A2) รวม login/register/logout
│ │ • A2: ฟังก์ชันต้องเขียน
│ │ - owner_register(): Response
│ │ - login(): Response (combined Owner/Admin + remember me)
│ │ - logout(): Response
│ └─ api/
│ └─ routes.py — (U3) /api/health (ขยายเมื่อมี API เพิ่ม)
│ • U3: ฟังก์ชันต้องเขียน
│ - api_health(): JSON Response
│
├─ models/
│ ├─ user.py — (A2) โครง user/admin (ORM)
│ ├─ property.py — (O2) Property/Image/Amenity/PropertyAmenity
│ └─ approval.py — (A1) ApprovalRequest, AuditLog (ต่อ workflow)
│ • A1: ฟังก์ชัน model-level (optional staticmethod/classmethod)
│ - AuditLog.log(actor_type:str, actor_id:int, action:str, property_id:int|None, meta:dict|None) -> None
│
├─ repositories/
│ ├─ interfaces/
│ │ ├─ user_repo.py — (A2) สัญญา repo user
│ │ ├─ property_repo.py — (U1) สัญญา repo property
│ │ └─ approval_repo.py — (A1) สัญญา repo approval/log (ต่อยอด)
│ └─ sqlalchemy/
│ ├─ user_repo_sql.py — (A2)
│ │ • A2: ฟังก์ชันต้องเขียน
│ │ - add_owner(owner:Owner) -> Owner
│ │ - get_owner_by_email(email:str) -> Owner|None
│ │ - get_admin_by_username(username:str) -> Admin|None
│ ├─ property_repo_sql.py — (U1 — หนัก) ค้นหา/ฟิลเตอร์จริง
│ │ • U1: ฟังก์ชันต้องเขียน
│ │ - get(prop_id:int) -> Property|None
│ │ - add(prop:Property) -> Property
│ │ - save(prop:Property) -> None
│ │ - list_approved(**filters) -> Query
│ │ (รองรับ q, min/max price, room_type, availability, amenities AND)
│ └─ approval_repo_sql.py — (A1) สำหรับ workflow
│ • A1: ฟังก์ชันต้องเขียน (แนะนำเพิ่ม)
│ - add_request(req:ApprovalRequest) -> ApprovalRequest
│ - update_request(req:ApprovalRequest) -> None
│ - add_log(log:AuditLog) -> AuditLog
│ - list_logs(page:int, per_page:int) -> Pagination
│
├─ services/
│ ├─ auth_service.py — (A2) สมัคร/ตรวจ/ล็อกอิน/ล็อกเอาต์
│ │ • A2: ฟังก์ชันต้องเขียน
│ │ - register_owner(data:dict) -> Owner
│ │ - verify_owner(email:str, password:str) -> bool
│ │ - login_owner(owner:Owner) -> None
│ │ - verify_admin(username:str, password:str) -> Admin|None
│ │ - login_admin(admin:Admin) -> None
│ │ - logout() -> None
│ ├─ property_service.py — (O1 — หนัก) จัดการประกาศ
│ │ • O1: ฟังก์ชันต้องเขียน
│ │ - create(owner_id:int, data:dict) -> Property
│ │ - update(owner_id:int, prop_id:int, data:dict) -> Property|None
│ ├─ search_service.py — (U1) เรียก repo + คำนวณหน้า
│ │ • U1: ฟังก์ชันต้องเขียน
│ │ - search(filters:dict, page:int=1, per_page:int=12) -> dict
│ ├─ approval_service.py — (A1 — หนัก) เวิร์กโฟลว์อนุมัติ
│ │ • A1: ฟังก์ชันต้องเขียน (แนะนำเพิ่ม)
│ │ - submit(prop:Property, owner_id:int) -> None
│ │ - approve(admin_id:int, prop_id:int, note:str|None) -> None
│ │ - reject(admin_id:int, prop_id:int, note:str|None) -> None
│ │ - get_logs(page:int=1, per_page:int=20) -> dict
│ ├─ upload_service.py — (O1) จัดเก็บรูป/ชื่อไฟล์
│ │ • O1: ฟังก์ชันต้องเขียน
│ │ - save_image(owner_id:int, file_storage) -> str
│ └─ policies/
│ └─ property_policy.py — (O2) นโยบาย
│ • O2: ฟังก์ชันต้องเขียน/ดูแลค่า
│ - can_upload_more(current_count:int) -> bool
│
├─ forms/
│ ├─ auth.py — (A2) ฟอร์มสมัคร/ล็อกอิน
│ ├─ owner.py — (O2) ฟอร์ม property + validate room_type
│ └─ upload.py — (O1) ฟอร์มอัปโหลด/จัดเรียงรูป
│
├─ utils/
│ └─ validation.py — (U2) helper validation
│ • U2: ฟังก์ชันต้องเขียน
│ - is_valid_citizen_id(cid:str) -> bool
│ - validate_image_file(fs, max_mb:int=3) -> None (raise ถ้าผิด)
│ - validate_pdf_file(fs, max_mb:int=10) -> None (raise ถ้าผิด)
│
└─ templates/ — (U3 + O1 + A1 ร่วมกัน)
├─ base.html — (U3) Navbar/flash
├─ public/ (U1/U3) — index.html, detail.html
├─ owner/ (O1/O2) — dashboard.html, form.html (drag&drop)
├─ admin/ (A1) — queue.html (+ approve/reject views)
└─ auth/ (A2) — login.html, owner_register.html

```

### สรุป “อย่างน้อย 1 ฟังก์ชัน/คน” (Checklist)

- **U1 (หนัก)**  
  - `SearchService.search()`  
  - `SqlPropertyRepo.list_approved()`  
  - `public.routes.index()`  
- **U2**  
  - `utils.validation.is_valid_citizen_id()` *(หรือ Map helper/ฝัง Google Maps ใน detail)*  
- **U3**  
  - `api.routes.api_health()`  
  - ปรับ `templates/base.html` + pagination partial/Jinja filter  
- **O1 (หนัก)**  
  - `PropertyService.create()` / `update()`  
  - Endpoints ใน `owner.routes` (upload/delete/reorder)  
  - `UploadService.save_image()`  
- **O2**  
  - `forms.owner.PropertyForm.validate_room_type()`  
  - `policies.property_policy.can_upload_more()`  
  - *(เสริม)* บันทึก amenities many-to-many ใน `owner.routes.edit_property`  
- **A1 (หนัก)**  
  - `ApprovalService.approve()` / `reject()` / `get_logs()`  
  - `admin.routes.approve()` / `reject()` / `logs()`  
  - `models.approval.AuditLog.log()`  
- **A2**  
  - `AuthService.register_owner()` / `verify_owner()` / `verify_admin()` / `login_owner()` / `login_admin()` / `logout()`  
  - `extensions.load_user()` + decorators (`owner_required` / `admin_required`)  
  - `auth.routes.login()` / `owner_register()` / `logout()`  
  - `__init__.py: register_dependencies()` + CLI seed (`seed_amenities`, `seed_sample`)  

---

## การติดตั้ง/รัน (Local)

> ต้องมี **Python 3.11/3.12** และ `pip`

```bash
pip install -r requirements.txt

# สร้างตารางฐานข้อมูล (ครั้งแรก)
flask --app run.py db init
flask --app run.py db migrate -m "init schema"
flask --app run.py db upgrade

# Seed ข้อมูลเริ่มต้น
flask --app run.py seed_amenities
flask --app run.py seed_sample

# รันเว็บ
python run.py
# เปิด http://127.0.0.1:5000/
บัญชีทดสอบ

Admin: admin / admin

Owner: owner@example.com / password (จาก seed_sample)

แนวทางร่วมงาน (Workflow)
1 feature = 1 branch: feature/u1-search, feature/o1-gallery, feature/a1-approval, …

แก้ models → ต้อง สร้าง migration ใหม่: db migrate + db upgrade และ commit โฟลเดอร์ migrations/

ยึด signature ของ Services/Repositories ตามสัญญา (interfaces) ลด conflict

ตั้ง pre-commit (black/ruff) เพื่อ format/lint ก่อน commit

ใช้ seed เดียวกันเพื่อเทสต์ร่วมกัน

Troubleshooting
Error: No such command 'db' → Flask import app ไม่ผ่าน; ดู traceback ด้านบนสุด, แก้ import ให้ผ่านก่อน

ModuleNotFoundError: app.forms.auth → สร้างไฟล์ app/forms/auth.py และทำ app/forms/__init__.py ให้เป็น namespace เปล่า

ValueError: blueprint name 'auth' is already registered → register blueprint ซ้ำ; เช็ค create_app()

IndentationError → ตรวจไฟล์เยื้องบรรทัด (ใช้ editor ที่โชว์ whitespace)

อัปโหลดรูปไม่สำเร็จ → ตรวจชนิด/ขนาดไฟล์, สิทธิ์เขียน UPLOAD_FOLDER

#การเเบ่งงาน

U1 (หนัก)

SearchService.search()

SqlPropertyRepo.list_approved()

public.routes.index()

U2

utils.validation.is_valid_citizen_id() (หรือ Map helper แปะ Google Maps ใน detail)

U3

api.routes.api_health()

ปรับ templates/base.html + pagination partial (ถ้าทำเป็นฟังก์ชัน Jinja filter ก็ได้)

O1 (หนัก)

PropertyService.create() / update()

owner.routes (upload/delete/reorder endpoints)

UploadService.save_image()

O2

forms.owner.PropertyForm.validate_room_type()

policies.property_policy.can_upload_more()

(เสริม) บันทึก amenities many-to-many ใน owner.routes.edit_property

A1 (หนัก)

ApprovalService.approve()/reject()/get_logs()

admin.routes.approve()/reject()/logs()

models.approval.AuditLog.log()

A2

AuthService.register_owner()/verify_owner()/verify_admin()/login_owner()/login_admin()/logout()

extensions.load_user() + decorators

auth.routes.login()/owner_register()/logout()

__init__.py: register_dependencies() + CLI seed

คน “หนัก” ทำ ≥3 ฟังก์ชัน; คนทั่วไปทำ ≥1 ฟังก์ชัน (แนะนำ 2)