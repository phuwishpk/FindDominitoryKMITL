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
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", (BASE_DIR / 'uploads').as_posix())
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    BABEL_DEFAULT_LOCALE = "th"
    BABEL_DEFAULT_TIMEZONE = "Asia/Bangkok"
