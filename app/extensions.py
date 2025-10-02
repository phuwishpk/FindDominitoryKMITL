from functools import wraps
from flask import abort
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# from .models import Owner, Admin # Import models ที่จำเป็น

# สร้าง instances ของ extensions เพื่อให้สามารถ import ไปใช้ในส่วนอื่นของ app ได้
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login" # กำหนดหน้า login route

@login_manager.user_loader
def load_user(user_id: str):
    """
    Flask-Login callback สำหรับโหลด user จาก session
    เราใช้ prefix 'owner-' หรือ 'admin-' เพื่อแยกว่าจะโหลดข้อมูลจาก table ไหน
    
    :param user_id: ID ของ user ที่ถูกเก็บใน session (เช่น 'owner-1' หรือ 'admin-1')
    :return: instance ของ Owner หรือ Admin, หรือ None
    """
    # from .repositories import OwnerRepository, AdminRepository # ควร get ผ่าน DI แต่ user_loader ทำไม่ได้ตรงๆ
    
    if user_id.startswith('owner-'):
        owner_id = int(user_id.split('-')[1])
        # หมายเหตุ: ในแอปจริงควรใช้ Repository pattern
        return db.session.get(Owner, owner_id)
    elif user_id.startswith('admin-'):
        admin_id = int(user_id.split('-')[1])
        return db.session.get(Admin, admin_id)
    return None

def owner_required(f):
    """
    Decorator สำหรับป้องกัน route ให้เข้าถึงได้เฉพาะ Owner ที่ login แล้ว
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Owner):
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator สำหรับป้องกัน route ให้เข้าถึงได้เฉพาะ Admin ที่ login แล้ว
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            abort(400) # Forbidden
        return f(*args, **kwargs)
    return decorated_function
