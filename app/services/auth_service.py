# app/services/auth_service.py
from __future__ import annotations

from typing import TYPE_CHECKING
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

from app.extensions import Principal
from app.repositories.interfaces.user_repo import IUserRepo
from app.services.upload_service import UploadService

if TYPE_CHECKING:
    # ใช้เฉพาะตอน type-check; ไม่รัน import ตอน runtime
    from app.models.user import Owner, Admin


class AuthService:
    def __init__(self, user_repo: IUserRepo, upload_service: UploadService):
        self.user_repo = user_repo
        self.upload_service = upload_service

    def register_owner(self, data: dict) -> "Owner":
        # ✅ lazy import เพื่อตัดวงจรอิมพอร์ต
        from app.models.user import Owner

        # แยกไฟล์ PDF (ถ้ามี)
        pdf_file = data.pop("occupancy_pdf", None)

        # สร้าง Owner (ยังไม่ใส่ path PDF)
        owner = Owner(
            full_name_th=data.get("full_name_th"),
            full_name_en=data.get("full_name_en"),
            citizen_id=data.get("citizen_id"),
            email=data.get("email"),
            phone=data.get("phone"),
            password_hash=generate_password_hash(data.get("password")),
        )

        # บันทึก เพื่อให้ได้ new_owner.id
        new_owner = self.user_repo.add_owner(owner)

        # อัปโหลด PDF (ถ้ามี) แล้วอัปเดต path กลับเข้าไป
        if pdf_file and getattr(pdf_file, "filename", None):
            try:
                pdf_path = self.upload_service.save_document(
                    owner_id=new_owner.id,
                    file_storage=pdf_file,
                )
                new_owner.occupancy_notice_pdf = pdf_path
                # ต้องมีเมธอดนี้ใน repo ของคุณ
                self.user_repo.save_owner(new_owner)
            except Exception as e:
                # dev log; พิจารณา logger จริงในโปรดักชัน
                print(f"Error uploading PDF for owner {new_owner.id}: {e}")

        return new_owner

    def verify_owner(self, email: str, password: str) -> bool:
        owner = self.user_repo.get_owner_by_email(email)
        return bool(owner and check_password_hash(owner.password_hash, password) and owner.is_active)

    def login_owner(self, owner: "Owner") -> None:
        principal = Principal(f"owner:{owner.id}", "owner", owner.id)
        login_user(principal, remember=True)

    def verify_admin(self, username: str, password: str) -> "Admin | None":
        admin = self.user_repo.get_admin_by_username(username)
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    def login_admin(self, admin: "Admin") -> None:
        principal = Principal(f"admin:{admin.id}", "admin", admin.id)
        login_user(principal, remember=True)

    def logout(self) -> None:
        logout_user()
