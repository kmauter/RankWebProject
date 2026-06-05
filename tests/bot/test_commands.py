"""Unit tests for bot/commands.py — /rank track and /rank untrack."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord import app_commands

from bot.commands import register_commands
from bot.store import ConfigStore


@pytest.fixture
def store(tmp_path):
    """Create a ConfigStore backed by a temp file."""
    config_path = tmp_path / "config.json"
    return ConfigStore(path=str(config_path))


@pytest.fixture
def api_client():
    """Create a mock API client."""
    client = AsyncMock()
    return client


@pytest.fixture
def rank_group(store, api_client):
    """Create a rank group with commands registered."""
    group = app_commands.Group(name="rank", description="Test rank group")
    register_commands(group, store, api_client)
    return group


@pytest.fixture
def interaction():
    """Create a mock Discord interaction."""
    inter = MagicMock()
    inter.guild_id = 123456789
    inter.channel_id = 987654321
    inter.response = AsyncMock()
    return inter


def _get_command(rank_group: app_commands.Group, name: str):
    """Get a command from the group by name."""
    for cmd in rank_group.commands:
        if cmd.name == name:
            return cmd
    raise ValueError(f"Command '{name}' not found in group")


class TestTrackCommand:
    """Tests for /rank track."""

    @pytest.mark.asyncio
    async def test_track_valid_game(self, rank_group, store, api_client, interaction):
        """Tracking a valid game adds it to the store and confirms."""
        api_client.get_game.return_value = {"title": "Summer Jams", "gameCode": "ABC123"}

        track_cmd = _get_command(rank_group, "track")
        await track_cmd.callback(interaction, game_code="ABC123")

        config = store.get_config(123456789)
        assert "ABC123" in config.tracked_games
        interaction.response.send_message.assert_called_once()
        msg = interaction.response.send_message.call_args[0][0]
        assert "Summer Jams" in msg
        assert "ABC123" in msg

    @pytest.mark.asyncio
    async def test_track_sets_notification_channel(self, rank_group, store, api_client, interaction):
        """Tracking sets the notification channel if not already configured (Req 8.1)."""
        api_client.get_game.return_value = {"title": "Test Game", "gameCode": "XYZ"}

        track_cmd = _get_command(rank_group, "track")
        await track_cmd.callback(interaction, game_code="XYZ")

        config = store.get_config(123456789)
        assert config.notification_channel_id == 987654321

    @pytest.mark.asyncio
    async def test_track_does_not_override_existing_channel(self, rank_group, store, api_client, interaction):
        """Tracking does not override an already-configured notification channel."""
        store.set_channel(123456789, 111111111)
        api_client.get_game.return_value = {"title": "Test Game", "gameCode": "XYZ"}

        track_cmd = _get_command(rank_group, "track")
        await track_cmd.callback(interaction, game_code="XYZ")

        config = store.get_config(123456789)
        assert config.notification_channel_id == 111111111

    @pytest.mark.asyncio
    async def test_track_game_not_found(self, rank_group, store, api_client, interaction):
        """Tracking a non-existent game responds with an error (Req 1.2)."""
        api_client.get_game.return_value = None

        track_cmd = _get_command(rank_group, "track")
        await track_cmd.callback(interaction, game_code="NOPE")

        config = store.get_config(123456789)
        assert "NOPE" not in config.tracked_games
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "not found" in msg.lower()

    @pytest.mark.asyncio
    async def test_track_already_tracked(self, rank_group, store, api_client, interaction):
        """Tracking an already-tracked game responds with 'already tracked' (Req 1.3)."""
        store.track_game(123456789, "ABC123")

        track_cmd = _get_command(rank_group, "track")
        await track_cmd.callback(interaction, game_code="ABC123")

        # API should not be called if already tracked
        api_client.get_game.assert_not_called()
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "already" in msg.lower()

    @pytest.mark.asyncio
    async def test_track_no_guild(self, rank_group, api_client, interaction):
        """Command in DMs responds with error."""
        interaction.guild_id = None

        track_cmd = _get_command(rank_group, "track")
        await track_cmd.callback(interaction, game_code="ABC123")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True


class TestUntrackCommand:
    """Tests for /rank untrack."""

    @pytest.mark.asyncio
    async def test_untrack_tracked_game(self, rank_group, store, interaction):
        """Untracking a tracked game removes it and confirms (Req 1.4)."""
        store.track_game(123456789, "ABC123")

        untrack_cmd = _get_command(rank_group, "untrack")
        await untrack_cmd.callback(interaction, game_code="ABC123")

        config = store.get_config(123456789)
        assert "ABC123" not in config.tracked_games
        interaction.response.send_message.assert_called_once()
        msg = interaction.response.send_message.call_args[0][0]
        assert "ABC123" in msg

    @pytest.mark.asyncio
    async def test_untrack_not_tracked(self, rank_group, store, interaction):
        """Untracking a non-tracked game responds with error (Req 1.5)."""
        untrack_cmd = _get_command(rank_group, "untrack")
        await untrack_cmd.callback(interaction, game_code="NOPE")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "not being tracked" in msg.lower()

    @pytest.mark.asyncio
    async def test_untrack_no_guild(self, rank_group, interaction):
        """Command in DMs responds with error."""
        interaction.guild_id = None

        untrack_cmd = _get_command(rank_group, "untrack")
        await untrack_cmd.callback(interaction, game_code="ABC123")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
