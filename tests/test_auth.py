"""
test_auth.py
------------
Automated test suite for testing ClipMind AI Authentication & JWT endpoints:
- Registration (POST /auth/register)
- Login & JWT Generation (POST /auth/login)
- Current User Profile (GET /auth/me)
- Role-Based Access Control (GET /auth/admin-check)
"""

import sys
import os

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_auth_flow():
    print("--- Starting Auth & JWT Integration Tests ---")

    # 1. Register a new Administrator user
    admin_payload = {
        "name": "Admin User",
        "email": "admin@clipmind.ai",
        "password": "Password123!",
        "role": "administrator"
    }

    res_reg = client.post("/auth/register", json=admin_payload)
    print(f"Register Admin Status: {res_reg.status_code}")
    assert res_reg.status_code in (201, 400), f"Unexpected status: {res_reg.status_code}"

    # 2. Register a Learner user
    learner_payload = {
        "name": "Learner User",
        "email": "learner@clipmind.ai",
        "password": "Password123!",
        "role": "learner"
    }
    client.post("/auth/register", json=learner_payload)

    # 3. Test Login with Admin User
    login_payload = {
        "email": "admin@clipmind.ai",
        "password": "Password123!"
    }
    res_login = client.post("/auth/login", json=login_payload)
    assert res_login.status_code == 200, f"Login failed: {res_login.json()}"
    token_data = res_login.json()
    assert "access_token" in token_data, "No access_token returned"
    admin_token = token_data["access_token"]
    print("Admin login successful, JWT token received!")

    # 4. Test Protected Profile Route (/auth/me)
    headers = {"Authorization": f"Bearer {admin_token}"}
    res_me = client.get("/auth/me", headers=headers)
    assert res_me.status_code == 200, f"Profile fetch failed: {res_me.json()}"
    profile = res_me.json()
    assert profile["email"] == "admin@clipmind.ai"
    assert profile["role"] == "administrator"
    print(f"Profile retrieved successfully: {profile['name']} ({profile['role']})")

    # 5. Test RBAC: Admin check with Admin Token (Should succeed)
    res_admin_check = client.get("/auth/admin-check", headers=headers)
    assert res_admin_check.status_code == 200, f"Admin check failed: {res_admin_check.json()}"
    print(f"RBAC Admin Check Output: {res_admin_check.json()['message']}")

    # 6. Test RBAC: Admin check with Learner Token (Should fail with 403 Forbidden)
    res_learner_login = client.post("/auth/login", json={
        "email": "learner@clipmind.ai",
        "password": "Password123!"
    })
    learner_token = res_learner_login.json()["access_token"]
    learner_headers = {"Authorization": f"Bearer {learner_token}"}

    res_forbidden = client.get("/auth/admin-check", headers=learner_headers)
    assert res_forbidden.status_code == 403, f"Expected 403 Forbidden, got {res_forbidden.status_code}"
    print("RBAC verification passed! Learner denied access to admin-only route with 403 Forbidden.")

    print("--- ALL AUTH & JWT TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_full_auth_flow()
