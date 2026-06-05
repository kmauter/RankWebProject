"""Tests for the webhook server endpoint (POST /notify)."""

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, TestClient, TestServer
from unittest.mock import AsyncMock, patch

from bot.store import ConfigStore
from bot.webhook_server import create_webhook_app


@pytest.fixture
def store(tmp_path):
    """Create a ConfigStore backed by a temp file."""
    config_path = tmp_path / "config.json"
    return ConfigStore(path=str(config_path))


@pytest.fixture
def webhook_app(store):
    """Create a webhook app with no dispatch handler (default)."""
    return create_webhook_app(store=store, api_client=None)


@pytest.fixture
def webhook_app_with_dispatch(store):
    """Create a webhook app with a mock dispatch handler."""
    dispatch = AsyncMock()
    app = create_webhook_app(
        store=store, api_client=None, dispatch_notification=dispatch
    )
    return app, dispatch


@pytest.fixture
async def client(webhook_app, aiohttp_client):
    """Create a test client for the webhook app."""
    return await aiohttp_client(webhook_app)


@pytest.fixture
async def client_with_dispatch(webhook_app_with_dispatch, aiohttp_client):
    """Create a test client with dispatch handler."""
    app, dispatch = webhook_app_with_dispatch
    cli = await aiohttp_client(app)
    return cli, dispatch


class TestWebhookNotifyEndpoint:
    """Tests for POST /notify."""

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_valid_request_returns_200(self, client):
        """A valid request with correct secret returns 200."""
        resp = await client.post("/notify", json={
            "game_code": "ABC123",
            "new_stage": "rankings",
            "secret": "test-secret",
        })
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_invalid_secret_returns_403(self, client):
        """An invalid secret returns 403 Forbidden."""
        resp = await client.post("/notify", json={
            "game_code": "ABC123",
            "new_stage": "rankings",
            "secret": "wrong-secret",
        })
        assert resp.status == 403
        data = await resp.json()
        assert "Forbidden" in data["error"]

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_missing_secret_returns_403(self, client):
        """A missing secret returns 403 Forbidden."""
        resp = await client.post("/notify", json={
            "game_code": "ABC123",
            "new_stage": "rankings",
        })
        assert resp.status == 403

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_missing_game_code_returns_400(self, client):
        """A payload missing game_code returns 400."""
        resp = await client.post("/notify", json={
            "new_stage": "rankings",
            "secret": "test-secret",
        })
        assert resp.status == 400
        data = await resp.json()
        assert "game_code" in data["error"]

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_missing_new_stage_returns_400(self, client):
        """A payload missing new_stage returns 400."""
        resp = await client.post("/notify", json={
            "game_code": "ABC123",
            "secret": "test-secret",
        })
        assert resp.status == 400
        data = await resp.json()
        assert "new_stage" in data["error"]

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_malformed_json_returns_400(self, client):
        """A request with invalid JSON returns 400."""
        resp = await client.post(
            "/notify",
            data=b"not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_notifies_tracking_servers(
        self, webhook_app_with_dispatch, aiohttp_client
    ):
        """Valid request dispatches notifications to all tracking servers."""
        app, dispatch = webhook_app_with_dispatch
        cli = await aiohttp_client(app)

        # Set up a server tracking the game
        store = app["store"]
        store.track_game(111, "ABC123")
        store.set_channel(111, 999)

        resp = await cli.post("/notify", json={
            "game_code": "ABC123",
            "new_stage": "rankings",
            "secret": "test-secret",
        })
        assert resp.status == 200
        data = await resp.json()
        assert data["notified"] == 1
        dispatch.assert_called_once()

        # Verify dispatch was called with the right args
        call_args = dispatch.call_args
        server_config = call_args[0][0]
        assert server_config.server_id == 111
        assert call_args[0][1] == "ABC123"
        assert call_args[0][2] == "rankings"

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_notifies_multiple_servers(
        self, webhook_app_with_dispatch, aiohttp_client
    ):
        """Valid request dispatches to all servers tracking the game."""
        app, dispatch = webhook_app_with_dispatch
        cli = await aiohttp_client(app)

        store = app["store"]
        store.track_game(111, "ABC123")
        store.set_channel(111, 999)
        store.track_game(222, "ABC123")
        store.set_channel(222, 888)

        resp = await cli.post("/notify", json={
            "game_code": "ABC123",
            "new_stage": "done",
            "secret": "test-secret",
        })
        assert resp.status == 200
        data = await resp.json()
        assert data["notified"] == 2
        assert dispatch.call_count == 2

    @patch("bot.webhook_server.BOT_NOTIFY_SECRET", "test-secret")
    async def test_no_servers_tracking_returns_zero(self, client):
        """When no servers track the game, notified count is 0."""
        resp = await client.post("/notify", json={
            "game_code": "UNKNOWN",
            "new_stage": "rankings",
            "secret": "test-secret",
        })
        assert resp.status == 200
        data = await resp.json()
        assert data["notified"] == 0
