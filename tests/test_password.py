"""
Tests for password management endpoints: forgot-password and change-password.
"""
import pytest
from tests.conftest import make_auth_header
from app.models import User
from app import db


class TestForgotPassword:
    """Tests for POST /api/forgot-password"""

    def test_forgot_password_by_email(self, client, sample_user):
        """Valid email resets password and returns new one."""
        original_hash = sample_user.password_hash
        resp = client.post("/api/forgot-password", json={"identifier": "test@example.com"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "new_password" in data
        assert len(data["new_password"]) == 12
        # Password should have changed
        db.session.refresh(sample_user)
        assert sample_user.password_hash != original_hash

    def test_forgot_password_by_username(self, client, sample_user):
        """Valid username also works."""
        resp = client.post("/api/forgot-password", json={"identifier": "testuser"})
        assert resp.status_code == 200
        assert "new_password" in resp.get_json()

    def test_forgot_password_nonexistent_user_returns_404(self, client):
        """Non-existent user returns 404."""
        resp = client.post("/api/forgot-password", json={"identifier": "nobody@example.com"})
        assert resp.status_code == 404

    def test_forgot_password_missing_identifier_returns_400(self, client):
        """Missing identifier returns 400."""
        resp = client.post("/api/forgot-password", json={"identifier": ""})
        assert resp.status_code == 400


class TestChangePassword:
    """Tests for POST /api/change-password"""

    def test_change_password_valid(self, client, sample_user):
        """Authenticated user can change their password."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/change-password", headers=headers, json={
            "old_password": "password123",
            "new_password": "newpassword456",
            "new_password2": "newpassword456",
        })
        assert resp.status_code == 200
        db.session.refresh(sample_user)
        assert sample_user.check_password("newpassword456")

    def test_change_password_wrong_old_password(self, client, sample_user):
        """Returns 403 if old password is wrong."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/change-password", headers=headers, json={
            "old_password": "wrongpassword",
            "new_password": "newpassword456",
            "new_password2": "newpassword456",
        })
        assert resp.status_code == 403
        assert "incorrect" in resp.get_json()["error"].lower()

    def test_change_password_mismatch(self, client, sample_user):
        """Returns 400 if new passwords don't match."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/change-password", headers=headers, json={
            "old_password": "password123",
            "new_password": "newpassword456",
            "new_password2": "different789",
        })
        assert resp.status_code == 400
        assert "do not match" in resp.get_json()["error"].lower()

    def test_change_password_too_short(self, client, sample_user):
        """Returns 400 if new password is too short."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/change-password", headers=headers, json={
            "old_password": "password123",
            "new_password": "abc",
            "new_password2": "abc",
        })
        assert resp.status_code == 400
        assert "6 characters" in resp.get_json()["error"].lower()

    def test_change_password_missing_fields(self, client, sample_user):
        """Returns 400 if any field is missing."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/change-password", headers=headers, json={
            "old_password": "password123",
        })
        assert resp.status_code == 400

    def test_change_password_requires_auth(self, client):
        """Returns 401 without authentication."""
        resp = client.post("/api/change-password", json={
            "old_password": "password123",
            "new_password": "newpassword456",
            "new_password2": "newpassword456",
        })
        assert resp.status_code == 401
