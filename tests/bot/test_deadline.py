"""Unit tests for bot/deadline.py — deadline detection and active game filtering."""

from datetime import date

from bot.deadline import ACTIVE_STAGES, filter_active_games, is_deadline_approaching


class TestIsDeadlineApproaching:
    """Tests for is_deadline_approaching(due_date, now)."""

    def test_due_today_returns_true(self):
        now = date(2025, 7, 10)
        due = date(2025, 7, 10)
        assert is_deadline_approaching(due, now) is True

    def test_due_tomorrow_returns_true(self):
        now = date(2025, 7, 10)
        due = date(2025, 7, 11)
        assert is_deadline_approaching(due, now) is True

    def test_due_yesterday_returns_false(self):
        now = date(2025, 7, 10)
        due = date(2025, 7, 9)
        assert is_deadline_approaching(due, now) is False

    def test_due_two_days_away_returns_false(self):
        now = date(2025, 7, 10)
        due = date(2025, 7, 12)
        assert is_deadline_approaching(due, now) is False

    def test_due_far_in_past_returns_false(self):
        now = date(2025, 7, 10)
        due = date(2025, 6, 1)
        assert is_deadline_approaching(due, now) is False

    def test_due_far_in_future_returns_false(self):
        now = date(2025, 7, 10)
        due = date(2025, 12, 25)
        assert is_deadline_approaching(due, now) is False


class TestFilterActiveGames:
    """Tests for filter_active_games(games)."""

    def test_filters_submissions_stage(self):
        games = [{"title": "Game A", "status": "submissions"}]
        result = filter_active_games(games)
        assert result == games

    def test_filters_rankings_stage(self):
        games = [{"title": "Game B", "status": "rankings"}]
        result = filter_active_games(games)
        assert result == games

    def test_excludes_done_stage(self):
        games = [{"title": "Game C", "status": "results"}]
        result = filter_active_games(games)
        assert result == []

    def test_mixed_stages(self):
        games = [
            {"title": "Active 1", "status": "submissions"},
            {"title": "Done", "status": "results"},
            {"title": "Active 2", "status": "rankings"},
        ]
        result = filter_active_games(games)
        assert len(result) == 2
        assert result[0]["title"] == "Active 1"
        assert result[1]["title"] == "Active 2"

    def test_empty_list(self):
        assert filter_active_games([]) == []

    def test_missing_status_key_excluded(self):
        games = [{"title": "No status"}]
        result = filter_active_games(games)
        assert result == []

    def test_active_stages_constant(self):
        assert ACTIVE_STAGES == {"submissions", "rankings"}
