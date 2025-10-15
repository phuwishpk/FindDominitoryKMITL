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
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "LIMITER_ENABLED": False, # <-- เพิ่มบรรทัดนี้เพื่อปิด Rate Limit ตอนเทส
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()