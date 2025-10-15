# tests/conftest.py

import pytest
from app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False, # ปิด CSRF token ในโหมดเทส
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()