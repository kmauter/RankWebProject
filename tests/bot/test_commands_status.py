"""Unit tests for /rank status and /rank active commands in bot/commands.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from bot.commands import _active_command, _status_command, register_commands
from bot.store import ConfigStore


@pytest.fixture
def store(tmp_path):
    """Create a ConfigStore backed by a temp file."""
    config_path = tmp_path / "config.json"
    return ConfigStore(path=str(config_path))


@pytest.fixture
def api_client():
    """Create a mock RankWebAPIClient."""
    client = AsyncMock()
    return client


@pytest.fixture(autouse=True)
def setup_commands(store, api_client):
    """Register commands with mocked dependencies."""
    group = MagicMock()
    group.add_command = MagicMock()
    register_commands(group, store, api_client)


def _make_interaction(guild_id: int = 123456789) -> MagicMock:
    """Create a mock Discord interaction."""
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.guild_id = guild_id
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    return interaction


class TestStatusCommand:
    """Tests for the /rank status subcommand."""

    @pytest.mark.asyncio
    async def test_no_tracked_games_sends_empty_message(self, store):
        """Req 2.2: If no games tracked, respond saying no games tracked."""
        interaction = _make_interaction()

        await _status_command.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "no games" in msg.lower() or "No games" in msg

    @pytest.mark.asyncio
    async def test_tracked_games_displays_status_embed(self, store, api_client):
        """Req 2.1: /rank status displays all tracked games."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")
        store.track_game(server_id, "GAME2")

        api_client.get_game.side_effect = [
            {"title": "Summer Jams", "status": "submissions", "submissionDueDate": "2025-07-01", "gameCode": "GAME1"},
            {"title": "Winter Hits", "status": "rankings", "rankDueDate": "2025-07-08", "gameCode": "GAME2"},
        ]

        interaction = _make_interaction(guild_id=server_id)

        await _status_command.callback(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()
        call_kwargs = interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert isinstance(embed, discord.Embed)

    @pytest.mark.asyncio
    async def test_api_returns_none_for_all_games(self, store, api_client):
        """When API can't fetch any games, show error message."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = None

        interaction = _make_interaction(guild_id=server_id)

        await _status_command.callback(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()
        msg = interaction.followup.send.call_args[0][0]
        assert "unable" in msg.lower() or "unavailable" in msg.lower()

    @pytest.mark.asyncio
    async def test_not_in_guild_sends_ephemeral_error(self, store):
        """Command used outside a server sends ephemeral error."""
        interaction = _make_interaction()
        interaction.guild_id = None

        await _status_command.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True


class TestActiveCommand:
    """Tests for the /rank active subcommand."""

    @pytest.mark.asyncio
    async def test_no_tracked_games_sends_empty_message(self, store):
        """Req 3.2: If no games tracked, respond accordingly."""
        interaction = _make_interaction()

        await _active_command.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "no games" in msg.lower() or "No games" in msg

    @pytest.mark.asyncio
    async def test_active_games_displayed(self, store, api_client):
        """Req 3.1: /rank active shows only SUBMIT/RANK stage games."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")
        store.track_game(server_id, "GAME2")

        api_client.get_game.side_effect = [
            {"title": "Summer Jams", "status": "submissions", "submissionDueDate": "2025-07-01", "gameCode": "GAME1"},
            {"title": "Winter Hits", "status": "results", "gameCode": "GAME2"},
        ]

        interaction = _make_interaction(guild_id=server_id)

        await _active_command.callback(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()
        call_kwargs = interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert isinstance(embed, discord.Embed)

    @pytest.mark.asyncio
    async def test_no_active_games_sends_message(self, store, api_client):
        """Req 3.2: If no active games, respond saying no active games."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = {
            "title": "Done Game", "status": "results", "gameCode": "GAME1"
        }

        interaction = _make_interaction(guild_id=server_id)

        await _active_command.callback(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()
        msg = interaction.followup.send.call_args[0][0]
        assert "no active" in msg.lower() or "No active" in msg

    @pytest.mark.asyncio
    async def test_api_returns_none_for_all_games(self, store, api_client):
        """When API can't fetch any games, show error message."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = None

        interaction = _make_interaction(guild_id=server_id)

        await _active_command.callback(interaction)

        interaction.response.defer.assert_called_once()
        interaction.followup.send.assert_called_once()
        msg = interaction.followup.send.call_args[0][0]
        assert "unable" in msg.lower() or "unavailable" in msg.lower()

    @pytest.mark.asyncio
    async def test_not_in_guild_sends_ephemeral_error(self, store):
        """Command used outside a server sends ephemeral error."""
        interaction = _make_interaction()
        interaction.guild_id = None

        await _active_command.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
