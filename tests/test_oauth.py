"""
Tests for OAuth flow endpoints: Spotify and YouTube connect + callback.

Per the testing plan, the correct behavior is:
- Connect endpoints should use JWT auth (not query param user_id)
- Callbacks should exchange code for tokens and store refresh token

The current implementation uses query param user_id (a P1 security issue),
so tests assert the correct JWT-based behavior and will fail until fixed.
"""
import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import make_auth_header
from app.models import User
from app import db


class TestConnectSpotify:
    """Tests for GET /api/connect-spotify"""

    def test_connect_spotify_redirects_to_auth_url(self, client, sample_user):
        """Connect Spotify with valid JWT returns auth URL."""
        headers = make_auth_header(sample_user.id)
        resp = client.get("/api/connect-spotify", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "auth_url" in data
        assert "accounts.spotify.com/authorize" in data["auth_url"]

    def test_connect_spotify_no_auth_returns_401(self, client):
        """Connect Spotify without auth returns 401."""
        resp = client.get("/api/connect-spotify")
        assert resp.status_code == 401


class TestSpotifyCallback:
    """Tests for GET /api/spotifycallback"""

    @patch("app.routes.requests.post")
    def test_callback_with_valid_code_stores_token(self, mock_post, client, sample_user):
        """Spotify callback with valid code stores refresh token on user."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake-access-token",
            "refresh_token": "fake-refresh-token",
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        resp = client.get(f"/api/spotifycallback?code=valid-code&state={sample_user.id}")
        assert resp.status_code == 200

        db.session.refresh(sample_user)
        assert sample_user.spotify_refresh_token == "fake-refresh-token"

    def test_callback_missing_code(self, client, sample_user):
        """Spotify callback without code returns 400."""
        resp = client.get(f"/api/spotifycallback?state={sample_user.id}")
        assert resp.status_code == 400

    def test_callback_missing_state(self, client):
        """Spotify callback without state returns 400."""
        resp = client.get("/api/spotifycallback?code=some-code")
        assert resp.status_code == 400

    @patch("app.routes.requests.post")
    def test_callback_token_exchange_fails(self, mock_post, client, sample_user):
        """Spotify callback when token exchange fails returns 400."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        resp = client.get(f"/api/spotifycallback?code=bad-code&state={sample_user.id}")
        assert resp.status_code == 400


class TestConnectYouTube:
    """Tests for GET /api/connect-youtube"""

    def test_connect_youtube_redirects_to_auth_url(self, client, sample_user):
        """Connect YouTube with valid JWT returns auth URL."""
        headers = make_auth_header(sample_user.id)
        resp = client.get("/api/connect-youtube", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "auth_url" in data
        assert "accounts.google.com" in data["auth_url"]

    def test_connect_youtube_no_auth_returns_401(self, client):
        """Connect YouTube without auth returns 401."""
        resp = client.get("/api/connect-youtube")
        assert resp.status_code == 401


class TestYouTubeCallback:
    """Tests for GET /api/youtubecallback"""

    @patch("app.routes.requests.post")
    def test_callback_with_valid_code_stores_token(self, mock_post, client, sample_user):
        """YouTube callback with valid code stores refresh token on user."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake-yt-access-token",
            "refresh_token": "fake-yt-refresh-token",
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        resp = client.get(f"/api/youtubecallback?code=valid-code&state={sample_user.id}")
        assert resp.status_code == 200

        db.session.refresh(sample_user)
        assert sample_user.youtube_refresh_token == "fake-yt-refresh-token"

    def test_callback_missing_code(self, client, sample_user):
        """YouTube callback without code returns 400."""
        resp = client.get(f"/api/youtubecallback?state={sample_user.id}")
        assert resp.status_code == 400

    def test_callback_missing_state(self, client):
        """YouTube callback without state returns 400."""
        resp = client.get("/api/youtubecallback?code=some-code")
        assert resp.status_code == 400

    @patch("app.routes.requests.post")
    def test_callback_token_exchange_fails(self, mock_post, client, sample_user):
        """YouTube callback when token exchange fails returns 400."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        resp = client.get(f"/api/youtubecallback?code=bad-code&state={sample_user.id}")
        assert resp.status_code == 400
