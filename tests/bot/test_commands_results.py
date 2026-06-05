"""Unit tests for /rank results command in bot/commands.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from bot.commands import _results_command, register_commands
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
    return interaction


class TestResultsCommand:
    """Tests for the /rank results subcommand."""

    @pytest.mark.asyncio
    async def test_game_not_tracked_sends_ephemeral_error(self, store):
        """Req 7.3: If game not tracked in server, respond with error."""
        interaction = _make_interaction()

        await _results_command.callback(interaction, game_code="NOTTRACKED")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
        msg = call_kwargs.get("content") or interaction.response.send_message.call_args[0][0]
        assert "not tracked" in msg.lower() or "NOTTRACKED" in msg

    @pytest.mark.asyncio
    async def test_game_not_done_sends_not_available(self, store, api_client):
        """Req 7.2: If game not in DONE stage, respond saying not yet available."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = {
            "title": "Summer Jams",
            "status": "rankings",
            "rankDueDate": "2025-07-08",
            "gameCode": "GAME1",
        }

        interaction = _make_interaction(guild_id=server_id)

        await _results_command.callback(interaction, game_code="GAME1")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "not yet available" in msg.lower()

    @pytest.mark.asyncio
    async def test_game_done_shows_results_embed(self, store, api_client):
        """Req 7.1: /rank results shows embed with song rankings."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = {
            "title": "Summer Jams",
            "status": "results",
            "gameCode": "GAME1",
        }
        api_client.get_game_songs.return_value = [
            {"title": "Song A", "artist": "Artist 1", "averageRank": 1.5},
            {"title": "Song B", "artist": "Artist 2", "averageRank": 2.3},
        ]

        interaction = _make_interaction(guild_id=server_id)

        await _results_command.callback(interaction, game_code="GAME1")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]
        assert isinstance(embed, discord.Embed)
        # Verify the embed contains song info
        assert "Summer Jams" in embed.title

    @pytest.mark.asyncio
    async def test_api_unreachable_sends_error(self, store, api_client):
        """When API can't fetch game data, show error message."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = None

        interaction = _make_interaction(guild_id=server_id)

        await _results_command.callback(interaction, game_code="GAME1")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "unable" in msg.lower() or "reach" in msg.lower()

    @pytest.mark.asyncio
    async def test_no_songs_sends_warning(self, store, api_client):
        """When game is done but API returns no songs, show warning."""
        server_id = 123456789
        store.track_game(server_id, "GAME1")

        api_client.get_game.return_value = {
            "title": "Summer Jams",
            "status": "results",
            "gameCode": "GAME1",
        }
        api_client.get_game_songs.return_value = []

        interaction = _make_interaction(guild_id=server_id)

        await _results_command.callback(interaction, game_code="GAME1")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "no song data" in msg.lower() or "GAME1" in msg

    @pytest.mark.asyncio
    async def test_not_in_guild_sends_ephemeral_error(self, store):
        """Command used outside a server sends ephemeral error."""
        interaction = _make_interaction()
        interaction.guild_id = None

        await _results_command.callback(interaction, game_code="GAME1")

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True
