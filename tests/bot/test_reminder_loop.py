"""Unit tests for the deadline reminder background task in bot.bot.RankBot."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.bot import RankBot
from bot.store import ConfigStore, ServerConfig


@pytest.fixture
def store(tmp_path):
    """Create a ConfigStore backed by a temp file."""
    config_path = tmp_path / "config.json"
    return ConfigStore(path=str(config_path))


@pytest.fixture
def bot(store):
    """Create a RankBot with mocked internals for testing."""
    with patch("bot.bot.DISCORD_BOT_TOKEN", "fake-token"):
        bot = RankBot.__new__(RankBot)
        bot.store = store
        bot.api_client = AsyncMock()
        return bot


class TestCheckGameDeadline:
    """Tests for RankBot._check_game_deadline."""

    @pytest.mark.asyncio
    async def test_sends_submit_reminder_when_deadline_approaching(self, bot, store):
        """When a game is in submissions and deadline is tomorrow, send reminder."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)
        store.set_role(1, 200)

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "submissions",
            "submissionDueDate": "2025-07-01",
            "gameCode": "GAME1",
        })

        channel = AsyncMock()
        today = date(2025, 6, 30)  # One day before deadline

        await bot._check_game_deadline(1, "GAME1", channel, "<@&200>", today)

        channel.send.assert_called_once()
        assert store.is_reminder_sent(1, "GAME1", "submit")

    @pytest.mark.asyncio
    async def test_sends_rank_reminder_when_deadline_approaching(self, bot, store):
        """When a game is in rankings and deadline is tomorrow, send reminder."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)
        store.set_role(1, 200)

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "rankings",
            "rankDueDate": "2025-07-08",
            "gameCode": "GAME1",
        })

        channel = AsyncMock()
        today = date(2025, 7, 7)  # One day before rank deadline

        await bot._check_game_deadline(1, "GAME1", channel, "<@&200>", today)

        channel.send.assert_called_once()
        assert store.is_reminder_sent(1, "GAME1", "rank")

    @pytest.mark.asyncio
    async def test_does_not_send_when_deadline_far_away(self, bot, store):
        """When deadline is more than 1 day away, no reminder is sent."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "submissions",
            "submissionDueDate": "2025-07-10",
            "gameCode": "GAME1",
        })

        channel = AsyncMock()
        today = date(2025, 7, 1)  # 9 days before deadline

        await bot._check_game_deadline(1, "GAME1", channel, "", today)

        channel.send.assert_not_called()
        assert not store.is_reminder_sent(1, "GAME1", "submit")

    @pytest.mark.asyncio
    async def test_does_not_send_duplicate_reminder(self, bot, store):
        """When reminder already sent, do not send again (dedup)."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)
        store.mark_reminder_sent(1, "GAME1", "submit")

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "submissions",
            "submissionDueDate": "2025-07-01",
            "gameCode": "GAME1",
        })

        channel = AsyncMock()
        today = date(2025, 6, 30)

        await bot._check_game_deadline(1, "GAME1", channel, "", today)

        channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_when_api_returns_none(self, bot, store):
        """When the API returns None (game not found), skip gracefully."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)

        bot.api_client.get_game = AsyncMock(return_value=None)

        channel = AsyncMock()
        today = date(2025, 7, 1)

        await bot._check_game_deadline(1, "GAME1", channel, "", today)

        channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_done_games(self, bot, store):
        """Games in done stage do not trigger reminders."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "results",
            "gameCode": "GAME1",
        })

        channel = AsyncMock()
        today = date(2025, 7, 1)

        await bot._check_game_deadline(1, "GAME1", channel, "", today)

        channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_invalid_due_date_gracefully(self, bot, store):
        """When due date string is invalid, skip without crashing."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "submissions",
            "submissionDueDate": "not-a-date",
            "gameCode": "GAME1",
        })

        channel = AsyncMock()
        today = date(2025, 7, 1)

        # Should not raise
        await bot._check_game_deadline(1, "GAME1", channel, "", today)

        channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_missing_due_date(self, bot, store):
        """When due date is missing from API response, skip gracefully."""
        store.track_game(1, "GAME1")
        store.set_channel(1, 100)

        bot.api_client.get_game = AsyncMock(return_value={
            "title": "Test Game",
            "status": "submissions",
            "gameCode": "GAME1",
            # submissionDueDate is missing
        })

        channel = AsyncMock()
        today = date(2025, 7, 1)

        await bot._check_game_deadline(1, "GAME1", channel, "", today)

        channel.send.assert_not_called()
