import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}"
    ).replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", (BASE_DIR / 'uploads').as_posix()) 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    BABEL_DEFAULT_LOCALE = "th"
    BABEL_DEFAULT_TIMEZONE = "Asia/Bangkok"

    # --- vvv แก้ไขการตั้งค่าอีเมลสำหรับทดสอบ vvv ---
    # ใช้เซิร์ฟเวอร์จำลองที่รันบนเครื่องของเรา
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 8025  # พอร์ตเดียวกับที่รันในขั้นตอนที่ 1
    MAIL_USE_TLS = False
    # ไม่ต้องใช้ Username/Password สำหรับเซิร์ฟเวอร์จำลอง
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = ('FindDorm KMITL', 'noreply@finddorm-kmitl.com')
    # --- ^^^ สิ้นสุดการแก้ไข ^^^ ---