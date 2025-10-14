import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    WTF_CSRF_ENABLED = True

    # *** ส่วนที่แก้ไข: ดึงค่าจาก ENV (ใช้สำหรับ PostgreSQL บน Render) ***
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}" # SQLite เป็นเพียง Fallback
    ).replace("postgres://", "postgresql://", 1) # แก้ไขสำหรับ SQLAlchemy 2.x

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # *** ส่วนที่แก้ไข: UPLOAD_FOLDER จะเป็นแบบชั่วคราว ***
    # แม้จะมีการตั้งค่า แต่ไฟล์ที่อัปโหลดจะถูกลบเมื่อ Deploy/Restart
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", (BASE_DIR / 'uploads').as_posix()) 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    BABEL_DEFAULT_LOCALE = "th"
    BABEL_DEFAULT_TIMEZONE = "Asia/Bangkok"