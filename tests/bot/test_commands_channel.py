"""Unit tests for bot/commands.py — /rank channel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

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
    return AsyncMock()


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
    inter.response = AsyncMock()
    return inter


def _get_command(rank_group: app_commands.Group, name: str):
    """Get a command from the group by name."""
    for cmd in rank_group.commands:
        if cmd.name == name:
            return cmd
    raise ValueError(f"Command '{name}' not found in group")


class TestChannelCommand:
    """Tests for /rank channel."""

    @pytest.mark.asyncio
    async def test_channel_sets_notification_channel(
        self, rank_group, store, interaction
    ):
        """Setting channel updates the store with the channel ID (Req 8.2)."""
        mock_channel = MagicMock()
        mock_channel.id = 555666777
        mock_channel.name = "bot-notifications"
        mock_channel.mention = "#bot-notifications"

        channel_cmd = _get_command(rank_group, "channel")
        await channel_cmd.callback(interaction, channel=mock_channel)

        config = store.get_config(123456789)
        assert config.notification_channel_id == 555666777

    @pytest.mark.asyncio
    async def test_channel_responds_with_confirmation(
        self, rank_group, store, interaction
    ):
        """Setting channel responds with a confirmation message."""
        mock_channel = MagicMock()
        mock_channel.id = 555666777
        mock_channel.name = "bot-notifications"
        mock_channel.mention = "#bot-notifications"

        channel_cmd = _get_command(rank_group, "channel")
        await channel_cmd.callback(interaction, channel=mock_channel)

        interaction.response.send_message.assert_called_once()
        msg = interaction.response.send_message.call_args[0][0]
        assert "#bot-notifications" in msg
        assert "notification" in msg.lower()

    @pytest.mark.asyncio
    async def test_channel_overrides_previous_channel(
        self, rank_group, store, interaction
    ):
        """Setting channel overrides any previously configured channel."""
        store.set_channel(123456789, 111222333)

        mock_channel = MagicMock()
        mock_channel.id = 444555666
        mock_channel.name = "new-channel"
        mock_channel.mention = "#new-channel"

        channel_cmd = _get_command(rank_group, "channel")
        await channel_cmd.callback(interaction, channel=mock_channel)

        config = store.get_config(123456789)
        assert config.notification_channel_id == 444555666

    @pytest.mark.asyncio
    async def test_channel_persists_to_store(
        self, rank_group, store, interaction, tmp_path
    ):
        """Setting channel persists the change via store.save() (Req 8.3)."""
        mock_channel = MagicMock()
        mock_channel.id = 555666777
        mock_channel.name = "bot-notifications"
        mock_channel.mention = "#bot-notifications"

        channel_cmd = _get_command(rank_group, "channel")
        await channel_cmd.callback(interaction, channel=mock_channel)

        # Reload store from disk to confirm persistence
        new_store = ConfigStore(path=str(tmp_path / "config.json"))
        new_store.load()
        config = new_store.get_config(123456789)
        assert config.notification_channel_id == 555666777
