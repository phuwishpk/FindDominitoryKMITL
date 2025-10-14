from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user
from flask_babel import Babel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from functools import wraps

# --- SQLAlchemy Engine Imports ---
from sqlalchemy.engine import Engine
from sqlalchemy import event
# --- End Imports ---

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
babel_ext = Babel() # 💡 แก้ไข: เปลี่ยนชื่อจาก babel
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()

class Principal(UserMixin):
    def __init__(self, sid: str, role: str, ref_id: int):
        self.id = sid
        self.role = role
        self.ref_id = ref_id

@login_manager.user_loader
def load_user(user_id: str):
    from app.models.user import Owner, Admin
    try:
        role, raw = user_id.split(":", 1)
        ref_id = int(raw)
    except Exception:
        return None
    if role == "owner":
        ent = Owner.query.get(ref_id)
        return Principal(user_id, "owner", ent.id) if ent else None
    if role == "admin":
        ent = Admin.query.get(ref_id)
        return Principal(user_id, "admin", ent.id) if ent else None
    return None

login_manager.login_view = "auth.login"

@login_manager.unauthorized_handler
def _unauth():
    from flask import request, redirect, url_for
    if request.path.startswith("/admin"):
        return redirect(url_for("auth.login", role="admin"))
    return redirect(url_for("auth.login", role="owner"))

def owner_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "owner":
            from flask import redirect, url_for
            return redirect(url_for("auth.login", role="owner"))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            from flask import redirect, url_for
            return redirect(url_for("auth.login", role="admin"))
        return f(*args, **kwargs)
    return wrapper

# --- vvv ส่วนที่แก้ไขเพื่อแก้ AttributeError vvv ---
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    เพิ่มฟังก์ชัน to_char เข้าไปใน SQLite DBAPI Connection เพื่อให้โค้ดที่ใช้ to_char
    ยังสามารถทำงานได้ในสภาพแวดล้อม SQLite (โดยใช้ strftime แทน)
    """
    # แก้ไข: เปลี่ยนมาตรวจสอบที่ connection_record.engine.dialect.name
    # เพื่อแก้ปัญหา AttributeError ที่เกิดขึ้นในบางเวอร์ชันของ SQLAlchemy
    try:
        is_sqlite = connection_record.engine.dialect.name == 'sqlite'
    except AttributeError:
        # Fallback: ใช้การตรวจสอบ driver name ซึ่งปลอดภัยกว่าใน context นี้
        is_sqlite = dbapi_connection.__class__.__name__ == 'Connection'

    if is_sqlite:
        
        def sqlite_to_char(value, format_str):
            # แปลงรูปแบบ 'YYYY-MM' (PostgreSQL style) เป็น '%Y-%m' (SQLite strftime style)
            sqlite_format = format_str.replace('YYYY', '%Y').replace('MM', '%m')
            
            cursor = dbapi_connection.cursor()
            try:
                # คำสั่ง SQL ที่รันจริงบน SQLite
                cursor.execute("SELECT strftime(?, ?)", (sqlite_format, value))
                return cursor.fetchone()[0]
            finally:
                cursor.close()

        # สร้างฟังก์ชัน to_char ใน SQLite connection
        dbapi_connection.create_function("to_char", 2, sqlite_to_char)
# --- ^^^ สิ้นสุดส่วนที่แก้ไข ^^^ ---
