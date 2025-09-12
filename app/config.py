import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    WTF_CSRF_ENABLED = True

    # SQLAlchemy — ใช้ SQLite ในโฟลเดอร์ instance/
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", (BASE_DIR / "uploads").as_posix())
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Babel (ตัวอย่าง)
    BABEL_DEFAULT_LOCALE = "th"
    BABEL_DEFAULT_TIMEZONE = "Asia/Bangkok"

    # Flask-Limiter (ตัวอย่างค่าเริ่มต้น)
