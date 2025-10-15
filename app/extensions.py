from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user
from flask_babel import Babel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
from functools import wraps
from flask_socketio import SocketIO, emit # <<< เพิ่ม: นำเข้า SocketIO, emit

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

# --- vvv เพิ่ม: SocketIO Initialization vvv ---
# กำหนดค่า cors_allowed_origins เป็น "*" เพื่อให้รับการเชื่อมต่อจากทุกโดเมน
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
# --- ^^^ สิ้นสุดการเพิ่ม ^^^ ---

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

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    เพิ่มฟังก์ชัน to_char เข้าไปใน SQLite DBAPI Connection เพื่อให้โค้ดที่ใช้ to_char
    ยังสามารถทำงานได้ในสภาพแวดล้อม SQLite (โดยใช้ strftime แทน)
    """
    try:
        is_sqlite = connection_record.engine.dialect.name == 'sqlite'
    except AttributeError:
        is_sqlite = dbapi_connection.__class__.__name__ == 'Connection'

    if is_sqlite:
        
        def sqlite_to_char(value, format_str):
            sqlite_format = format_str.replace('YYYY', '%Y').replace('MM', '%m')
            
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("SELECT strftime(?, ?)", (sqlite_format, value))
                return cursor.fetchone()[0]
            finally:
                cursor.close()

        dbapi_connection.create_function("to_char", 2, sqlite_to_char)
