import hashlib
from typing import Optional
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_principal import Identity, identity_changed

# สมมติว่ามีการ import models และ repositories ที่จำเป็น
# In a real app, these would be in separate files e.g., app/models.py, app/repositories.py
from ..models import Owner, Admin
from ..repositories import OwnerRepository, AdminRepository

class AuthService:
    """
    Service class for handling authentication logic for both Owners and Admins.
    """
    def __init__(self, owner_repo: OwnerRepository, admin_repo: AdminRepository):
        self.owner_repo = owner_repo
        self.admin_repo = admin_repo

    def register_owner(self, data: dict) -> Owner:
        """
        สมัคร owner ใหม่
        - ตรวจสอบข้อมูล (validate) เช่น email ซ้ำซ้อน
        - แฮชรหัสผ่าน (hash password)
        - บันทึกเส้นทางไฟล์ PDF (ถ้ามี)
        - บันทึกลงฐานข้อมูล
        """
        email = data.get('email')
        if self.owner_repo.find_by_email(email):
            raise ValueError(f"Owner with email {email} already exists.")

        password = data.get('password')
        if not password:
            raise ValueError("Password is required.")

        hashed_password = generate_password_hash(password)

        new_owner = Owner(
            email=email,
            password_hash=hashed_password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            id_card_pdf_path=data.get('id_card_pdf_path') # รับ path มาโดยตรง
        )

        self.owner_repo.add(new_owner)
        return new_owner

    def verify_owner(self, email: str, password: str) -> Optional[Owner]:
        """
        ตรวจสอบอีเมลและรหัสผ่านของ owner
        - ค้นหา owner จาก email
        - ถ้าเจอ ให้เปรียบเทียบรหัสผ่านที่ hash ไว้
        - คืนค่า Owner object ถ้าถูกต้อง, มิฉะนั้นคืนค่า None
        """
        owner = self.owner_repo.find_by_email(email)
        if owner and check_password_hash(owner.password_hash, password):
            return owner
        return None

    def login_owner(self, owner: Owner) -> None:
        """
        สร้าง session สำหรับ owner โดยใช้ Flask-Login
        และกำหนด identity สำหรับ Flask-Principal
        """
        login_user(owner)
        # บอก Flask-Principal ว่า identity ของ user ปัจจุบันมีการเปลี่ยนแปลง
        identity_changed.send(current_app._get_current_object(), identity=Identity(owner.id, 'owner'))


    def verify_admin(self, username: str, password: str) -> Optional[Admin]:
        """
        ตรวจสอบ username และรหัสผ่านของ admin
        - ค้นหา admin จาก username
        - ถ้าเจอ ให้เปรียบเทียบรหัสผ่านที่ hash ไว้
        - คืนค่า Admin object ถ้าถูกต้อง, มิฉะนั้นคืนค่า None
        """
        admin = self.admin_repo.find_by_username(username)
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    def login_admin(self, admin: Admin) -> None:
        """
        สร้าง session สำหรับ admin โดยใช้ Flask-Login
        และกำหนด identity สำหรับ Flask-Principal
        """
        login_user(admin)
        # บอก Flask-Principal ว่า identity ของ user ปัจจุบันมีการเปลี่ยนแปลง
        identity_changed.send(current_app._get_current_object(), identity=Identity(admin.id, 'admin'))


    def logout(self) -> None:
        """
        ออกจากระบบ (ล้าง session)
        - ใช้ logout_user ของ Flask-Login
        - ล้าง identity ของ Flask-Principal
        """
        logout_user()
        # ล้าง identity ที่เก็บไว้
        identity_changed.send(current_app._get_current_object(), identity=Identity(None, None))
