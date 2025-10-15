# tests/conftest.py

import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # ใช้ DB ใน Memory เพื่อความเร็ว
    })

    with app.app_context():
        _db.create_all() # สร้างตารางทั้งหมดใน DB สำหรับเทส
        yield app
        _db.drop_all() # ลบตารางทั้งหมดหลังเทสเสร็จ

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()