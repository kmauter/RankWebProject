"""
Tests for authentication endpoints: /api/register and /api/login, plus
protected route access with JWT tokens.
"""
import pytest
from tests.conftest import make_auth_header
from app.models import User
from app import db


class TestRegister:
    """Tests for POST /api/register"""

    def test_register_valid(self, client):
        """Register with valid data creates user and returns 201."""
        resp = client.post("/api/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass",
            "password2": "securepass",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data is not None  # Should return JSON, not plain text

        # Verify user exists in DB
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.email == "new@example.com"

    def test_register_mismatched_passwords(self, client):
        """Register with mismatched passwords returns 400."""
        resp = client.post("/api/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password1",
            "password2": "password2",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert "Passwords do not match" in data.get("error", "")

    def test_register_existing_username(self, client, sample_user):
        """Register with existing username returns 400."""
        resp = client.post("/api/register", json={
            "username": "testuser",  # same as sample_user
            "email": "different@example.com",
            "password": "password123",
            "password2": "password123",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert "User already exists" in data.get("error", "")

    def test_register_empty_username(self, client):
        """Register with empty username returns 400."""
        resp = client.post("/api/register", json={
            "username": "",
            "email": "new@example.com",
            "password": "pass",
            "password2": "pass",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data is not None  # Should return JSON error


class TestLogin:
    """Tests for POST /api/login"""

    def test_login_valid(self, client, sample_user):
        """Login with correct credentials returns JWT token."""
        resp = client.post("/api/login", json={
            "username": "testuser",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["message"] == "Login successful!"
        assert "token" in data
        assert data["user_id"] == sample_user.id

    def test_login_wrong_password(self, client, sample_user):
        """Login with wrong password returns 401."""
        resp = client.post("/api/login", json={
            "username": "testuser",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401
        data = resp.get_json()
        assert data["message"] == "Invalid username or password"

    def test_login_nonexistent_user(self, client):
        """Login with non-existent username returns 401."""
        resp = client.post("/api/login", json={
            "username": "nobody",
            "password": "password123",
        })
        assert resp.status_code == 401
        data = resp.get_json()
        assert data["message"] == "Invalid username or password"


class TestProtectedRoutes:
    """Tests for JWT-protected route access using /api/user-profile as the test endpoint."""

    def test_valid_token(self, client, sample_user):
        """Access with valid token returns user data."""
        headers = make_auth_header(sample_user.id)
        resp = client.get("/api/user-profile", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_expired_token(self, client, sample_user):
        """Access with expired token returns 401."""
        headers = make_auth_header(sample_user.id, expired=True)
        resp = client.get("/api/user-profile", headers=headers)
        assert resp.status_code == 401
        data = resp.get_json()
        assert "expired" in data.get("message", "").lower() or "expired" in str(data).lower()

    def test_no_token(self, client):
        """Access with no Authorization header returns 401."""
        resp = client.get("/api/user-profile")
        assert resp.status_code == 401

    def test_malformed_token(self, client):
        """Access with malformed token returns 401."""
        headers = {"Authorization": "Bearer not-a-real-token"}
        resp = client.get("/api/user-profile", headers=headers)
        assert resp.status_code == 401

    def test_wrong_secret_token(self, client, sample_user):
        """Token signed with wrong secret is rejected."""
        headers = make_auth_header(sample_user.id, secret="wrong-secret")
        resp = client.get("/api/user-profile", headers=headers)
        assert resp.status_code == 401
