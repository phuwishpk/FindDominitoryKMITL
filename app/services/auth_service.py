import os
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# สมมติว่ามีการ import models และ repositories ที่จำเป็น
# from ..models import Owner, Admin
# from ..repositories import OwnerRepository, AdminRepository

class AuthService:
    """
    คลาสสำหรับจัดการกระบวนการ Authentication ทั้งหมด
    - การลงทะเบียน, การเข้าสู่ระบบ, การออกจากระบบ
    - การตรวจสอบสิทธิ์ของ Owner และ Admin
    """
    def __init__(self, owner_repository, admin_repository):
        """
        Constructor รับ dependencies (Repositories) ผ่าน Dependency Injection.
        
        :param owner_repository: Repository สำหรับจัดการข้อมูล Owner
        :param admin_repository: Repository สำหรับจัดการข้อมูล Admin
        """
        self.owner_repository = owner_repository
        self.admin_repository = admin_repository

    def register_owner(self, data: dict) -> 'Owner':
        """
        สมัครสมาชิกสำหรับ Owner ใหม่
        - ตรวจสอบข้อมูล
        - Hash รหัสผ่าน
        - บันทึก path ของไฟล์ PDF (ถ้ามี)
        - บันทึกลงฐานข้อมูล
        
        :param data: dict ที่มีข้อมูลของ owner
        :return: instance ของ Owner ที่ถูกสร้างขึ้น
        """
        # TODO: เพิ่มการ Validate ข้อมูลที่เข้ามา (เช่น ใช้ Marshmallow หรือ Pydantic)
        if self.owner_repository.find_by_email(data['email']):
            raise ValueError("อีเมลนี้ถูกใช้งานแล้ว")

        hashed_password = generate_password_hash(data['password'])
        
        # สมมติว่า model Owner รับ parameter ตามนี้
        new_owner = self.owner_repository.create(
            email=data['email'],
            password_hash=hashed_password,
            first_name=data['first_name'],
            last_name=data['last_name'],
            # บันทึก path ของ PDF ถ้ามี, หรือเป็น None
            business_license_pdf_path=data.get('business_license_pdf_path') 
        )
        return new_owner

    def verify_owner(self, email: str, password: str) -> 'Owner' | None:
        """
        ตรวจสอบอีเมลและรหัสผ่านของ Owner
        
        :param email: อีเมลของ owner
        :param password: รหัสผ่าน
        :return: instance ของ Owner ถ้าข้อมูลถูกต้อง, มิฉะนั้นคืนค่า None
        """
        owner = self.owner_repository.find_by_email(email)
        if owner and check_password_hash(owner.password_hash, password):
            return owner
        return None

    def login_owner(self, owner: 'Owner') -> None:
        """
        สร้าง Session สำหรับ Owner โดยใช้ Flask-Login
        
        :param owner: instance ของ Owner ที่ผ่านการ verify แล้ว
        """
        # remember=True เพื่อให้ session คงอยู่หลังปิด browser
        login_user(owner, remember=True)

    def verify_admin(self, username: str, password: str) -> 'Admin' | None:
        """
        ตรวจสอบ Username และรหัสผ่านของ Admin
        
        :param username: Username ของ admin
        :param password: รหัสผ่าน
        :return: instance ของ Admin ถ้าข้อมูลถูกต้อง, มิฉะนั้นคืนค่า None
        """
        admin = self.admin_repository.find_by_username(username)
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    def login_admin(self, admin: 'Admin') -> None:
        """
        สร้าง Session สำหรับ Admin โดยใช้ Flask-Login
        
        :param admin: instance ของ Admin ที่ผ่านการ verify แล้ว
        """
        login_user(admin, remember=True)

    def logout(self) -> None:
        """
        ออกจากระบบ (Clear session) สำหรับ user ปัจจุบัน
        """
        logout_user()
