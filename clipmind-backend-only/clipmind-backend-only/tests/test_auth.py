"""
test_auth.py
------------
Basic tests for registration and login.

Run karne ke liye (backend/ folder ke andar se):
    pip install pytest httpx
    pytest ../tests/test_auth.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    # 1. Register a new user
    register_payload = {
        "name": "Test User",
        "email": "testuser_module1@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "role": "learner",
    }
    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code in (201, 400)  # 400 if user already exists from a previous run

    # 2. Login with the same credentials
    login_payload = {"email": "testuser_module1@example.com", "password": "password123"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "testuser_module1@example.com"


def test_login_with_wrong_password_fails():
    login_payload = {"email": "testuser_module1@example.com", "password": "wrongpassword"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401


def test_protected_route_without_token_fails():
    response = client.get("/api/dashboard/")
    assert response.status_code == 401
