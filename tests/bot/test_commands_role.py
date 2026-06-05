"""Unit tests for bot/commands.py — /rank join and /rank leave."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import discord
import pytest
from discord import app_commands

from bot.commands import register_commands, RANKER_ROLE_NAME
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


def _make_role(name="Ranker", role_id=111222333):
    """Create a mock Discord role."""
    role = MagicMock(spec=discord.Role)
    role.name = name
    role.id = role_id
    return role


def _make_interaction(guild=None, member=None):
    """Create a mock Discord interaction with guild and member."""
    interaction = MagicMock()
    interaction.guild = guild
    interaction.user = member
    interaction.response = AsyncMock()
    return interaction


def _make_guild(guild_id=123456789, roles=None):
    """Create a mock Discord guild."""
    guild = MagicMock(spec=discord.Guild)
    guild.id = guild_id
    guild.roles = roles or []
    guild.create_role = AsyncMock()
    return guild


def _make_member(roles=None):
    """Create a mock Discord Member."""
    member = MagicMock(spec=discord.Member)
    member.roles = roles or []
    member.add_roles = AsyncMock()
    member.remove_roles = AsyncMock()
    return member


def _get_command(rank_group: app_commands.Group, name: str):
    """Get a command from the group by name."""
    for cmd in rank_group.commands:
        if cmd.name == name:
            return cmd
    raise ValueError(f"Command '{name}' not found in group")


class TestJoinCommand:
    """Tests for /rank join."""

    @pytest.mark.asyncio
    async def test_join_creates_role_when_missing(self, rank_group, store):
        """If no Ranker role exists, creates one and assigns it (Req 4.3)."""
        new_role = _make_role()
        guild = _make_guild(roles=[])
        guild.create_role.return_value = new_role
        member = _make_member(roles=[])
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=None):
            join_cmd = _get_command(rank_group, "join")
            await join_cmd.callback(interaction)

        guild.create_role.assert_called_once_with(
            name=RANKER_ROLE_NAME,
            reason="Created by RankBot for game notifications",
        )
        member.add_roles.assert_called_once()
        config = store.get_config(123456789)
        assert config.ranker_role_id == new_role.id
        interaction.response.send_message.assert_called_once()
        msg = interaction.response.send_message.call_args[0][0]
        assert "Ranker" in msg

    @pytest.mark.asyncio
    async def test_join_uses_existing_role(self, rank_group, store):
        """If Ranker role exists, uses it without creating a new one (Req 4.2)."""
        existing_role = _make_role()
        guild = _make_guild(roles=[existing_role])
        member = _make_member(roles=[])
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=existing_role):
            join_cmd = _get_command(rank_group, "join")
            await join_cmd.callback(interaction)

        guild.create_role.assert_not_called()
        member.add_roles.assert_called_once()
        config = store.get_config(123456789)
        assert config.ranker_role_id == existing_role.id

    @pytest.mark.asyncio
    async def test_join_already_has_role(self, rank_group, store):
        """If user already has the Ranker role, responds with info message."""
        existing_role = _make_role()
        guild = _make_guild(roles=[existing_role])
        member = _make_member(roles=[existing_role])
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=existing_role):
            join_cmd = _get_command(rank_group, "join")
            await join_cmd.callback(interaction)

        member.add_roles.assert_not_called()
        interaction.response.send_message.assert_called_once()
        msg = interaction.response.send_message.call_args[0][0]
        assert "already" in msg.lower()

    @pytest.mark.asyncio
    async def test_join_missing_permission(self, rank_group, store):
        """If bot lacks Manage Roles permission, responds with helpful error."""
        guild = _make_guild(roles=[])
        guild.create_role.side_effect = discord.Forbidden(
            MagicMock(status=403), "Missing Permissions"
        )
        member = _make_member(roles=[])
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=None):
            join_cmd = _get_command(rank_group, "join")
            await join_cmd.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "Manage Roles" in msg

    @pytest.mark.asyncio
    async def test_join_no_guild(self, rank_group):
        """Command used outside a guild responds with error."""
        interaction = _make_interaction(guild=None, member=MagicMock())

        join_cmd = _get_command(rank_group, "join")
        await join_cmd.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True


class TestLeaveCommand:
    """Tests for /rank leave."""

    @pytest.mark.asyncio
    async def test_leave_removes_role(self, rank_group):
        """Leaving removes the Ranker role from the user (Req 4.4)."""
        ranker_role = _make_role()
        guild = _make_guild(roles=[ranker_role])
        member = _make_member(roles=[ranker_role])
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=ranker_role):
            leave_cmd = _get_command(rank_group, "leave")
            await leave_cmd.callback(interaction)

        member.remove_roles.assert_called_once()
        interaction.response.send_message.assert_called_once()
        msg = interaction.response.send_message.call_args[0][0]
        assert "removed" in msg.lower()

    @pytest.mark.asyncio
    async def test_leave_without_role(self, rank_group):
        """If user doesn't have Ranker role, responds with error (Req 4.5)."""
        ranker_role = _make_role()
        guild = _make_guild(roles=[ranker_role])
        member = _make_member(roles=[])  # No roles
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=ranker_role):
            leave_cmd = _get_command(rank_group, "leave")
            await leave_cmd.callback(interaction)

        member.remove_roles.assert_not_called()
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "don't have" in msg.lower()

    @pytest.mark.asyncio
    async def test_leave_role_not_in_guild(self, rank_group):
        """If Ranker role doesn't exist in guild, responds with error (Req 4.5)."""
        guild = _make_guild(roles=[])
        member = _make_member(roles=[])
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=None):
            leave_cmd = _get_command(rank_group, "leave")
            await leave_cmd.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "don't have" in msg.lower()

    @pytest.mark.asyncio
    async def test_leave_missing_permission(self, rank_group):
        """If bot lacks Manage Roles permission on leave, responds with error."""
        ranker_role = _make_role()
        guild = _make_guild(roles=[ranker_role])
        member = _make_member(roles=[ranker_role])
        member.remove_roles.side_effect = discord.Forbidden(
            MagicMock(status=403), "Missing Permissions"
        )
        interaction = _make_interaction(guild=guild, member=member)

        with patch("bot.commands.discord.utils.get", return_value=ranker_role):
            leave_cmd = _get_command(rank_group, "leave")
            await leave_cmd.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
        msg = interaction.response.send_message.call_args[0][0]
        assert "Manage Roles" in msg

    @pytest.mark.asyncio
    async def test_leave_no_guild(self, rank_group):
        """Command used outside a guild responds with error."""
        interaction = _make_interaction(guild=None, member=MagicMock())

        leave_cmd = _get_command(rank_group, "leave")
        await leave_cmd.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True
