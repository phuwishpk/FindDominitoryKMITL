from functools import wraps
from flask import current_app
from flask_login import LoginManager, current_user
from flask_principal import Principal, Permission, RoleNeed, UserNeed, identity_loaded

# --- สมมติว่ามีการ import models และ repositories ---
# ปกติจะ import มาจากไฟล์อื่น
from .repositories import OwnerRepository, AdminRepository

# 1. สร้าง instances ของ extensions
login_manager = LoginManager()
principal = Principal()

# 2. สร้าง "Needs" (ความต้องการ) สำหรับแต่ละบทบาท
# RoleNeed ต้องการแค่ชื่อบทบาท
admin_need = RoleNeed('admin')
owner_need = RoleNeed('owner')

# 3. สร้าง "Permissions" (สิทธิ์) จาก Needs
# Permission คือการตรวจสอบว่า user ปัจจุบันมี Need ที่กำหนดหรือไม่
admin_permission = Permission(admin_need)
owner_permission = Permission(owner_need)


@login_manager.user_loader
def load_user(user_id: str):
    """
    โหลด principal (Owner/Admin) จากฐานข้อมูลเพื่อผูกกับ session
    Flask-Login จะเรียกใช้ฟังก์ชันนี้ทุกครั้งที่มี request เข้ามา
    เพื่อโหลด user object จาก user_id ที่เก็บไว้ใน session

    เราใช้ prefix 'owner_' และ 'admin_' เพื่อแยกแยะระหว่างสองตาราง
    """
    container = current_app.config.get("container")
    if not container:
        return None

    owner_repo: OwnerRepository = container.get("owner_repository")
    admin_repo: AdminRepository = container.get("admin_repository")

    if user_id.startswith('owner_'):
        owner_id = int(user_id.split('_')[1])
        return owner_repo.find_by_id(owner_id)
    elif user_id.startswith('admin_'):
        admin_id = int(user_id.split('_')[1])
        return admin_repo.find_by_id(admin_id)
    return None

@identity_loaded.connect_via(current_app)
def on_identity_loaded(sender, identity):
    """
    หลังจาก identity ถูกโหลด (ตอน login), เราจะผูก Needs เข้ากับ identity นั้น
    เพื่อให้ Permission ทำงานได้
    """
    # identity.provides.add(UserNeed(identity.id)) # เพิ่ม UserNeed ถ้าต้องการเช็คสิทธิ์เฉพาะบุคคล

    # ตรวจสอบว่า user ที่ login อยู่เป็นประเภทไหน แล้วเพิ่ม RoleNeed ที่เหมาะสม
    if hasattr(current_user, 'role'):
        identity.provides.add(RoleNeed(current_user.role))


# --- Decorators สำหรับป้องกัน Route ---

def owner_required(f):
    """
    Decorator สำหรับป้องกันการเข้าถึง route ให้เฉพาะ Owner เท่านั้น
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ใช้ context manager ของ permission เพื่อตรวจสอบสิทธิ์
        with owner_permission.require(http_exception=403):
            return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator สำหรับป้องกันการเข้าถึง route ให้เฉพาะ Admin เท่านั้น
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with admin_permission.require(http_exception=403):
            return f(*args, **kwargs)
    return decorated_function
