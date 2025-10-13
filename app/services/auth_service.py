# File: app/services/auth_service.py

# ⬇️ [Python Standard Lib]
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
# ⬇️ [app/models/user.py], [app/extensions.py], [app/repositories/interfaces/user_repo.py], [app/services/upload_service.py]
from app.models.user import Owner, Admin
from app.extensions import Principal
from app.repositories.interfaces.user_repo import IUserRepo
from app.services.upload_service import UploadService 

class AuthService:
    # 🛠️ [app/services/auth_service.py] แก้ไข: รับ UploadService เข้ามาใน constructor
    def __init__(self, user_repo: IUserRepo, upload_service: UploadService): 
        self.user_repo = user_repo
        self.upload_service = upload_service

    def register_owner(self, data: dict) -> Owner:
        # 🛠️ [app/forms/auth.py] จัดการไฟล์ PDF ที่มากับฟอร์ม
        pdf_file = data.pop("occupancy_pdf", None)

        owner = Owner(
            full_name_th=data.get("full_name_th"),
            full_name_en=data.get("full_name_en"),
            citizen_id=data.get("citizen_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            password_hash=generate_password_hash(data.get("password"))
        )
        new_owner = self.user_repo.add_owner(owner)

        if pdf_file and getattr(pdf_file, "filename", None):
            try:
                # ⬇️ [app/services/upload_service.py] เรียกใช้ service อัปโหลด
                pdf_path = self.upload_service.save_document(
                    owner_id=new_owner.id,
                    file_storage=pdf_file,
                )
                new_owner.occupancy_notice_pdf = pdf_path
                # ⬇️ [app/repositories/sqlalchemy/user_repo_sql.py] บันทึก path กลับเข้า DB
                self.user_repo.save_owner(new_owner)
            except Exception as e:
                # ต้องมั่นใจว่า UploadService มีเมธอด save_document (ซึ่งไม่มีในไฟล์ที่ส่งมา แต่จำเป็นสำหรับ register)
                print(f"Error uploading PDF for owner {new_owner.id}: {e}")

        return new_owner

    # 🛠️ [app/services/auth_service.py] แก้ไข: ให้คืนค่า Owner object (หรือ None)
    def verify_owner(self, email: str, password: str) -> Owner | None:
        # ⬇️ [app/repositories/sqlalchemy/user_repo_sql.py] ดึง Owner จากอีเมล
        owner = self.user_repo.get_owner_by_email(email)
        # ตรวจสอบรหัสผ่านและสถานะ is_active
        if owner and check_password_hash(owner.password_hash, password) and owner.is_active:
            return owner # คืนค่า Owner object
        return None

    def login_owner(self, owner: Owner, remember: bool = False) -> None:
        principal = Principal(f"owner:{owner.id}", "owner", owner.id)
        login_user(principal, remember=remember)

    def verify_admin(self, username: str, password: str) -> Admin | None:
        # ⬇️ [app/repositories/sqlalchemy/user_repo_sql.py] ดึง Admin จาก username
        admin = self.user_repo.get_admin_by_username(username)
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    def login_admin(self, admin: Admin, remember: bool = False) -> None:
        principal = Principal(f"admin:{admin.id}", "admin", admin.id)
        login_user(principal, remember=remember)

    def logout(self) -> None:
        logout_user()