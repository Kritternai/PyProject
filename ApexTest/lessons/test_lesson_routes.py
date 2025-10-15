import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from flask import Flask
from app.routes.lesson_routes import lesson_bp


@pytest.fixture
def app():
    """สร้าง Flask app สำหรับทดสอบ blueprint"""
    app = Flask(__name__)
    app.register_blueprint(lesson_bp)
    return app
@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


# ---------- MOCK LOGIN REQUIRED DECORATOR ----------
@pytest.fixture(autouse=True)
def patch_login_required(monkeypatch):
    """แทนที่ login_required ให้ข้ามการตรวจสอบ auth"""
    def fake_login_required(func):
        return func
    monkeypatch.setattr('app.middleware.auth_middleware.login_required', fake_login_required)