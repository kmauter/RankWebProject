"""Tests for notification dispatch logic (bot/dispatch.py)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from bot.dispatch import create_dispatch_notification, _build_role_mention, _get_notification_embed
from bot.store import ServerConfig


@pytest.fixture
def mock_bot():
    """Create a mock bot instance."""
    bot = MagicMock()
    bot.get_channel = MagicMock()
    return bot


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = AsyncMock()
    return client


@pytest.fixture
def server_config():
    """Create a sample server config."""
    return ServerConfig(
        server_id=12345,
        tracked_games={"GAME1"},
        notification_channel_id=99999,
        ranker_role_id=77777,
    )


@pytest.fixture
def game_data():
    """Sample game data from the API."""
    return {
        "id": 1,
        "title": "Summer Jams",
        "status": "rankings",
        "description": "Best summer songs",
        "submissionDueDate": "2025-07-01",
        "rankDueDate": "2025-07-08",
        "gameCode": "GAME1",
        "spotifyPlaylistUrl": "https://open.spotify.com/playlist/123",
        "youtubePlaylistUrl": "https://youtube.com/playlist/456",
    }


class TestBuildRoleMention:
    """Tests for _build_role_mention helper."""

    def test_with_role_id(self):
        """Returns proper mention format when role ID is set."""
        assert _build_role_mention(77777) == "<@&77777>"

    def test_with_none(self):
        """Returns empty string when role ID is None."""
        assert _build_role_mention(None) == ""

    def test_with_zero(self):
        """Returns empty string when role ID is falsy (0)."""
        assert _build_role_mention(0) == ""


class TestGetNotificationEmbed:
    """Tests for _get_notification_embed helper."""

    def test_rankings_stage(self, game_data):
        """Returns rank open embed for 'rankings' stage."""
        embed = _get_notification_embed(game_data, "<@&77777>", "rankings")
        assert embed is not None
        assert "Ranking Open" in embed.title
        assert "Summer Jams" in embed.title

    def test_done_stage(self, game_data):
        """Returns results available embed for 'done' stage."""
        embed = _get_notification_embed(game_data, "<@&77777>", "done")
        assert embed is not None
        assert "Results Available" in embed.title
        assert "Summer Jams" in embed.title

    def test_unknown_stage(self, game_data):
        """Returns None for unknown stages."""
        embed = _get_notification_embed(game_data, "<@&77777>", "unknown_stage")
        assert embed is None


class TestDispatchNotification:
    """Tests for the dispatch_notification closure."""

    async def test_successful_rankings_notification(
        self, mock_bot, mock_api_client, server_config, game_data
    ):
        """Sends ranking notification to the correct channel."""
        mock_channel = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        await dispatch(server_config, "GAME1", "rankings")

        mock_api_client.get_game.assert_called_once_with("GAME1")
        mock_bot.get_channel.assert_called_once_with(99999)
        mock_channel.send.assert_called_once()

        # Verify the send call included content (role mention) and embed
        call_kwargs = mock_channel.send.call_args[1]
        assert call_kwargs["content"] == "<@&77777>"
        assert isinstance(call_kwargs["embed"], discord.Embed)

    async def test_successful_done_notification(
        self, mock_bot, mock_api_client, server_config, game_data
    ):
        """Sends results notification for 'done' stage."""
        mock_channel = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        await dispatch(server_config, "GAME1", "done")

        mock_channel.send.assert_called_once()
        call_kwargs = mock_channel.send.call_args[1]
        assert "Results Available" in call_kwargs["embed"].title

    async def test_no_notification_channel_configured(
        self, mock_bot, mock_api_client, game_data
    ):
        """Skips notification when no channel is configured."""
        config = ServerConfig(
            server_id=12345,
            tracked_games={"GAME1"},
            notification_channel_id=None,
            ranker_role_id=77777,
        )

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        await dispatch(config, "GAME1", "rankings")

        # Should not attempt to fetch game data or get channel
        mock_api_client.get_game.assert_not_called()
        mock_bot.get_channel.assert_not_called()

    async def test_game_not_found_in_api(
        self, mock_bot, mock_api_client, server_config
    ):
        """Skips notification when API returns None for the game."""
        mock_api_client.get_game.return_value = None

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        await dispatch(server_config, "GAME1", "rankings")

        mock_bot.get_channel.assert_not_called()

    async def test_channel_deleted(
        self, mock_bot, mock_api_client, server_config, game_data
    ):
        """Handles deleted channel gracefully (get_channel returns None)."""
        mock_bot.get_channel.return_value = None
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        # Should not raise
        await dispatch(server_config, "GAME1", "rankings")

    async def test_bot_lacks_send_permission(
        self, mock_bot, mock_api_client, server_config, game_data
    ):
        """Handles Forbidden error gracefully when bot can't send."""
        mock_channel = AsyncMock()
        mock_channel.send.side_effect = discord.Forbidden(
            MagicMock(status=403), "Missing Permissions"
        )
        mock_bot.get_channel.return_value = mock_channel
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        # Should not raise
        await dispatch(server_config, "GAME1", "rankings")

    async def test_channel_not_found_error(
        self, mock_bot, mock_api_client, server_config, game_data
    ):
        """Handles NotFound error gracefully when channel no longer exists."""
        mock_channel = AsyncMock()
        mock_channel.send.side_effect = discord.NotFound(
            MagicMock(status=404), "Unknown Channel"
        )
        mock_bot.get_channel.return_value = mock_channel
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        # Should not raise
        await dispatch(server_config, "GAME1", "rankings")

    async def test_unknown_stage_does_not_send(
        self, mock_bot, mock_api_client, server_config, game_data
    ):
        """Does not send notification for unknown stages."""
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        await dispatch(server_config, "GAME1", "submissions")

        mock_bot.get_channel.assert_not_called()

    async def test_no_role_id_sends_empty_mention(
        self, mock_bot, mock_api_client, game_data
    ):
        """When no role ID is configured, sends with empty content."""
        config = ServerConfig(
            server_id=12345,
            tracked_games={"GAME1"},
            notification_channel_id=99999,
            ranker_role_id=None,
        )
        mock_channel = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_api_client.get_game.return_value = game_data

        dispatch = create_dispatch_notification(mock_bot, mock_api_client)
        await dispatch(config, "GAME1", "rankings")

        call_kwargs = mock_channel.send.call_args[1]
        assert call_kwargs["content"] == ""
