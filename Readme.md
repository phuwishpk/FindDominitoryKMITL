# FindDormitoryKMITL — ระบบค้นหา/ประกาศหอพัก

โครงงาน **"เว็บค้นหาหอพัก KMITL"** จัดทำขึ้นเพื่อช่วยเหลือให้นักศึกษาสามารถค้นหาหอพักบริเวณสถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง (KMITL) ได้อย่างสะดวก รวดเร็ว และตอบโจทย์ความต้องการ

## 🎯 วัตถุประสงค์
- อำนวยความสะดวกแก่นักศึกษาในการค้นหาหอพักรอบ KMITL อย่างง่ายดายและมีประสิทธิภาพ  
- นำเสนอข้อมูลสำคัญของหอพัก เช่น ที่ตั้ง ราคา สิ่งอำนวยความสะดวก ค่ามัดจำ ระยะทางจากสถาบัน รวมถึงรูปภาพประกอบ  
- พัฒนาระบบค้นหาและการกรองข้อมูลที่ยืดหยุ่น เช่น การค้นหาตามช่วงราคา ประเภทหอพัก (ชาย/หญิง/รวม) หรือสิ่งอำนวยความสะดวก  
- ลดเวลาและความยุ่งยากในการตัดสินใจ รวมถึงช่วยให้นักศึกษาใหม่หรือผู้ปกครองไม่จำเป็นต้องสำรวจพื้นที่จริงมากนัก  
- ส่งเสริมการใช้เทคโนโลยีดิจิทัลเพื่อยกระดับคุณภาพชีวิตของนักศึกษาให้ดียิ่งขึ้น  

## 👥 คณะผู้จัดทำ
- **นาย ภูวิชญ์ ประกอบจิตร 67030183**
- **นาย กร แดงทอง 67030268**
- **นาย ธนบดี บุญภมร 67030298**
- **นาย พรพรม แจ่มจัง 67030323**
- **นางสาว ภิญญาพัชญ์ บานบัว 67030334**
- **นาย อัฐวุฒิ บัวเรียน 67030359**
- **นาย อิทธิพัทธิ์ สุทธินวล 67030360**

> ระบบตัวอย่างสำหรับค้นหาและประกาศหอพัก โดยแยกบทบาท **User / Owner / Admin** พัฒนาด้วย **Flask + SQLAlchemy + WTForms + Flask-Login + Bootstrap** พร้อมสถาปัตยกรรมแบบแยกชั้น (Layers) ชัดเจน

---

## ภาพรวมระบบ
**FindDormitoryKMITL** เป็นระบบค้นหา/ประกาศหอพัก โดยแยกบทบาทผู้ใช้งานเป็น 3 กลุ่ม:
- **User**: เข้าดูประกาศที่ผ่านการอนุมัติ (approved) พร้อมฟิลเตอร์ค้นหา
- **Owner**: สมัคร/ล็อกอิน สร้าง/แก้ไขประกาศ อัปโหลด/ลบ/ลากเรียงรูป (สูงสุด 6)
- **Admin**: ล็อกอิน จัดการคิวอนุมัติ (สามารถต่อยอด workflow และ audit log)

---

## บทบาทและคุณสมบัติหลัก
### User
- หน้าแสดงรายการประกาศที่มีสถานะ **approved**
- ฟิลเตอร์หลัก: ค้นหาข้อความ, ราคา, ประเภทห้อง, สิ่งอำนวยความสะดวก (amenities), สถานะห้อง (availability), ใกล้พิกัด (near/radius), เรียงลำดับ (sort)

### Owner
- สมัคร/ล็อกอินด้วย **อีเมล + รหัสผ่าน** (รองรับ remember me)
- จัดการประกาศ: ชื่อหอ, ประเภทห้อง, ช่องทางติดต่อ, ค่าใช้จ่าย, พิกัด, ลิงก์, สถานะห้อง
- แกลเลอรีรูป: อัปโหลด/ลบ/ลากเรียง (สูงสุด 6 รูป, ประเภท jpg/jpeg/png/webp, ขนาด ≤ 3MB/รูป)

### Admin (เริ่มต้น/ต่อยอด)
- ล็อกอินด้วย **username + รหัสผ่าน**
- จัดการคิวอนุมัติ, เปลี่ยน workflow, บันทึก AuditLog (วางโครงไว้สำหรับต่อยอด)

---

## สแตก/ไลบรารีที่ใช้
- **Flask 3.x**, **Werkzeug 3.x**
- **Flask-SQLAlchemy** + **SQLAlchemy 2.x**
- **Flask-Migrate (Alembic)**
- **Flask-WTF + WTForms**
- **Flask-Login**
- **Flask-Babel** (ตั้งค่า locale/timezone)
- **Flask-Limiter** (กัน brute force ในอนาคต)
- **Bootstrap 5 (CDN)**

---

## หน้าเริ่มต้นและ Navbar
- หน้าเริ่มต้น: **User** (รายการประกาศที่อนุมัติแล้ว)
- **Navbar**: ปุ่ม **Login** → ไปหน้า Login รวม (เลือก Owner/Admin)

---

## Authentication
- **Owner**: สมัคร/ล็อกอิน (อีเมล + รหัสผ่าน)
- **Admin**: ล็อกอิน (username + รหัสผ่าน)
- รองรับ **“จำการเข้าสู่ระบบ” (remember me)**

---

## Validation
- ตรวจ **บัตรประชาชนไทย 13 หลัก** (checksum)
- ตรวจไฟล์ **PDF** สำหรับเอกสารแจ้งมีผู้เข้าพัก (นามสกุล `.pdf`, ขนาด ≤ 10MB)
- ตรวจไฟล์ **รูปภาพ** (นามสกุลที่อนุญาต: jpg/jpeg/png/webp + ขนาด ≤ 3MB/รูป)

---

## ภาพรวมสถาปัตยกรรม
แนวคิดแยกชั้น (Layers):
- **Presentation**: Flask Blueprints + Templates (หน้าเว็บ, ฟอร์ม, routing)
- **Services**: ธุรกิจ/กฎเกณฑ์ (login, ค้นหา, อัปโหลด ฯลฯ)
- **Repositories**: Data Access ด้วย SQLAlchemy
- **Models (ORM)**: โครงสร้างตาราง/ความสัมพันธ์
- **Utils (Helper/Validation)**: ฟังก์ชันช่วยเหลือ (ตรวจบัตรประชาชน, ตรวจไฟล์)
- **Extensions/Config**: ตัวเชื่อม framework และ config รวมถึง DI container

---

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

# รันเว็บ (ทำการrunเเค่นี้ก็พอ)
python run.py 
# เปิด http://127.0.0.1:5000/
บัญชีทดสอบ
```
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


---

# การเเบ่งงาน

มาตรฐาน:
- **ฟังก์ชัน**: `snake_case`, verb-first, สื่อความชัดเจน
- **Branch**: `feat|fix|refactor|chore/<area>-<scope>-<owner>` (เช่น `feat/user-search-u1`)

---

## U1 (หนัก) — User Search/List

**ไฟล์ & ฟังก์ชัน**
- `app/services/search_service.py`
  - `search_properties(filters: dict, page: int = 1, per_page: int = 12) -> dict`  
    _อธิบาย_: รวมตรรกะค้นหา: แปลง query string → filters ที่ repo รองรับ, เรียก repo, จัดหน้า (pagination), คืน `{items, total, page, per_page, pages}`

- `app/repositories/sqlalchemy/property_repo_sql.py`
  - `list_approved_with_filters(**filters)`  
    _อธิบาย_: คืน SQLAlchemy Query ของประกาศที่ `workflow_status='approved'` พร้อมฟิลเตอร์ `q`, `price_min/max`, `room_type`, `availability`, `amenities AND`, `ordering` (ถ้ามี) — ไม่ execute เพื่อให้ service คุม paginate เอง

- `app/blueprints/public/routes.py`
  - `index()`  
    _อธิบาย_: รับ query-string จากผู้ใช้ (เช่น `?q=&min=&max=&amenities=...`), ส่งต่อให้ `search_properties`, render `templates/public/index.html`
  - `property_detail(prop_id: int)`  
    _อธิบาย_: ดึงประกาศ 1 รายการ (approved เท่านั้น) พร้อมรูป/amenities, render หน้า detail

**Branch**
- `feat/user-search-u1`
- *(ย่อย)* `feat/user-filters-u1`, `feat/user-pagination-u1`

---

## U2 — User Map/Detail & Validation

**ไฟล์ & ฟังก์ชัน**
- `app/utils/validation.py`
  - `is_valid_citizen_id(cid: str) -> bool`  
    _อธิบาย_: ตรวจรูปแบบและคำนวณ checksum 13 หลักสำหรับเลขบัตร ป้องกันสมัครด้วยเลขผิด
- *(ตัวเลือก Map helper สำหรับหน้า detail)*
  - `app/blueprints/public/helpers.py`
    - `build_gmap_embed(lat: float, lng: float, place_id: str | None = None) -> str`  
      _อธิบาย_: สร้าง URL/HTML embed ของ Google Maps จากพิกัด (หรือ place_id) ให้ template ฝังง่าย

**Branch**
- `feat/user-detail-map-u2`
- *(ย่อย)* `feat/utils-validation-u2`

---

## U3 — User UI/Base/API Health

**ไฟล์ & ฟังก์ชัน**
- `app/blueprints/api/routes.py`
  - `api_health()`  
    _อธิบาย_: Endpoint สุขภาพระบบ: คืน JSON เช่น `{"status":"ok","version":...}` เพื่อตรวจ uptime/health check

- `app/templates/base.html`  
  _อธิบาย_: วาง Navbar, Flash messages, Footer, slot ของ pagination/filters ให้ทุกหน้าใช้ร่วมกัน

- *(ตัวเลือก Jinja helpers — ถ้าทำ)*
  - `app/blueprints/public/jinja_filters.py`
    - `register_jinja_filters(app)`  
      _อธิบาย_: ลงทะเบียนฟิลเตอร์ Jinja ทั้งหมดสำหรับส่วน Public
    - `format_price(value)`  
      _อธิบาย_: แสดงราคาพร้อมคอมมา/หน่วย
    - `paginate_links(pagination)`  
      _อธิบาย_: สร้างลิงก์หน้า ก่อน/ถัดไป จากอ็อบเจ็กต์ pagination

**Branch**
- `feat/user-ui-base-u3`
- *(ย่อย)* `feat/user-pagination-u3`, `feat/api-health-u3`

---

## O1 (หนัก) — Owner CRUD + Gallery

**ไฟล์ & ฟังก์ชัน**
- `app/services/property_service.py`
  - `create_property(owner_id: int, data: dict) -> Property`  
    _อธิบาย_: ตรวจสิทธิ์/นโยบายเบื้องต้น สร้าง Property ใหม่, บันทึกฐานข้อมูล, คืนอ็อบเจ็กต์
  - `update_property(owner_id: int, prop_id: int, data: dict) -> Property | None`  
    _อธิบาย_: ตรวจว่าเป็นเจ้าของตัวจริงและยังแก้ไขได้, อัปเดตฟิลด์ที่อนุญาต, save

- `app/services/upload_service.py`
  - `save_property_image(owner_id: int, file_storage) -> str`  
    _อธิบาย_: ตรวจชนิด/ขนาดไฟล์รูป, ตั้งชื่อไฟล์ปลอดภัย, บันทึกลง `uploads/<owner_id>/images/`, คืน relative path

- `app/blueprints/owner/routes.py`
  - `dashboard()`  
    _อธิบาย_: แสดงรายการประกาศของ owner คนปัจจุบัน + สถิติสั้น ๆ
  - `new_property()`  
    _อธิบาย_: แสดง/รับฟอร์มสร้าง, ใช้ `PropertyService.create_property`
  - `edit_property(prop_id: int)`  
    _อธิบาย_: แก้ไขข้อมูลประกาศ + ส่วนจัดการรูป/amenities
  - `upload_property_image(prop_id: int)`  
    _อธิบาย_: อัปโหลดรูป (ตรวจ quota ≤ 6 รูป), เพิ่ม `PropertyImage` ใหม่, รีเทิร์น JSON/redirect
  - `delete_property_image(prop_id: int, image_id: int)`  
    _อธิบาย_: ลบรูป (ฐานข้อมูล + ไฟล์จริง), reindex `position`
  - `reorder_property_images(prop_id: int)`  
    _อธิบาย_: รับลำดับใหม่ (เช่น list ของ image_id), อัปเดต `position` ตาม drag & drop

**Branch**
- `feat/owner-crud-gallery-o1`
- *(ย่อย)* `feat/owner-upload-image-o1`, `feat/owner-reorder-images-o1`

---

## O2 — Owner Form & Amenities

**ไฟล์ & ฟังก์ชัน**
- `app/forms/owner.py`
  - `PropertyForm.validate_room_type(self, field)`  
    _อธิบาย_: ตรวจว่า room_type อยู่ในชุดที่อนุญาต (เช่น `studio`, `1br`, …) ป้องกันค่าแปลก

- `app/services/policies/property_policy.py`
  - `can_upload_more(current_count: int) -> bool`  
    _อธิบาย_: นโยบายจำกัดจำนวนรูป/ประกาศ (เช่น สูงสุด 6), ใช้ใน upload endpoint

- *(เสริม M2M amenities)*
  - `app/services/property_service.py`
    - `update_property_amenities(prop: Property, amenity_codes: list[str]) -> None`  
      _อธิบาย_: map ชุดโค้ด → เอนทิตี Amenity, sync ตารางเชื่อม `property_amenities` (add/remove ให้ตรง)

**Branch**
- `feat/owner-form-amenities-o2`
- *(ย่อย)* `feat/owner-policy-upload-limit-o2`

---

## A1 (หนัก) — Admin Approval Workflow

**ไฟล์ & ฟังก์ชัน**
- `app/services/approval_service.py`
  - `submit_property(property_id: int, owner_id: int) -> None`  
    _อธิบาย_: Owner ส่งขออนุมัติ: สร้าง/อัปเดต `approval_requests`, ตั้ง `workflow_status='submitted'`
  - `approve_property(admin_id: int, prop_id: int, note: str | None = None) -> None`  
    _อธิบาย_: อนุมัติโดย admin: ตั้ง `workflow_status='approved'`, ปิดคำขอ, บันทึก `AuditLog`
  - `reject_property(admin_id: int, prop_id: int, note: str | None = None) -> None`  
    _อธิบาย_: ปฏิเสธ: ตั้ง `workflow_status='rejected'`, เหตุผลใน note, ล็อกกิจกรรม
  - `get_audit_logs(page: int = 1, per_page: int = 20) -> dict`  
    _อธิบาย_: ดึงบันทึกกิจกรรมแบบแบ่งหน้า เพื่อแสดงใน UI ผู้ดูแล

- `app/blueprints/admin/routes.py`
  - `queue()`  
    _อธิบาย_: แสดงรายการ `submitted` รออนุมัติ
  - `approve(prop_id: int)` / `reject(prop_id: int)`  
    _อธิบาย_: เรียก service เปลี่ยนสถานะ พร้อมบันทึก note (ถ้ามี)
  - `logs(page: int = 1)`  
    _อธิบาย_: แสดง AuditLog แบบ paginate

- `app/models/approval.py`
  - `AuditLog.log(actor_type, actor_id, action, property_id=None, meta=None)`  
    _อธิบาย_: method สร้างบันทึกกิจกรรมส่วนกลาง ใช้ซ้ำได้ทุกที่

**Branch**
- `feat/admin-approval-workflow-a1`
- *(ย่อย)* `feat/admin-logs-a1`, `feat/admin-queue-a1`

---

## A2 — Auth/Security/DI/Seeds

**ไฟล์ & ฟังก์ชัน**
- `app/services/auth_service.py`
  - `register_owner(data: dict) -> Owner`  
    _อธิบาย_: สมัคร owner ใหม่: validate, hash password, บันทึก PDF path (ถ้ามี), เซฟ DB
  - `verify_owner(email: str, password: str) -> bool`  
    _อธิบาย_: ตรวจรหัสผ่าน owner
  - `login_owner(owner: Owner) -> None`  
    _อธิบาย_: ใช้ `login_user(...)` (Flask-Login) สร้าง session
  - `verify_admin(username: str, password: str) -> Admin | None`  
    _อธิบาย_: ตรวจรหัสผ่าน admin
  - `login_admin(admin: Admin) -> None`  
    _อธิบาย_: login user แบบ admin principal
  - `logout() -> None`  
    _อธิบาย_: ออกจากระบบ (clear session)

- `app/extensions.py`
  - `load_user(user_id: str) -> Principal | None`  
    _อธิบาย_: โหลด principal จากฐานข้อมูล (owner/admin) เพื่อผูกกับ session
  - `owner_required(f)` / `admin_required(f)`  
    _อธิบาย_: decorator ป้องกันการเข้าถึง route ตามบทบาท

- `app/__init__.py`
  - `register_dependencies(app) -> None`  
    _อธิบาย_: ผูก DI: services → repositories (SQLAlchemy) ใน `app.config["container"]`
  - `seed_amenities()` / `seed_sample()` (CLI)  
    _อธิบาย_: เติม master data (amenities) และข้อมูลตัวอย่าง (admin/owner/property)

**Branch**
- `feat/admin-auth-security-a2`
- *(ย่อย)* `feat/di-container-a2`, `feat/cli-seeds-a2`

---

## โครงสร้างชื่อ Commit/PR (แนะนำ)

- **Commit**: `feat(scope): action detail`  
  _ตัวอย่าง_: `feat(search): add amenities AND-filter + pagination`
- **PR Title**: ตรงกับ commit แรก + ใส่โค้ดคนทำ  
  _ตัวอย่าง_: `feat(search): add filters & approved listing (U1)`

---
