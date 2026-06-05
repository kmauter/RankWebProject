"""Unit tests for bot.store module."""

import json
import pytest

from bot.store import ConfigStore, ServerConfig


class TestServerConfig:
    """Tests for the ServerConfig dataclass."""

    def test_default_values(self):
        config = ServerConfig(server_id=123)
        assert config.server_id == 123
        assert config.tracked_games == set()
        assert config.notification_channel_id is None
        assert config.ranker_role_id is None
        assert config.reminders_sent == set()

    def test_custom_values(self):
        config = ServerConfig(
            server_id=456,
            tracked_games={"ABC", "XYZ"},
            notification_channel_id=789,
            ranker_role_id=111,
            reminders_sent={"ABC:submit"},
        )
        assert config.server_id == 456
        assert config.tracked_games == {"ABC", "XYZ"}
        assert config.notification_channel_id == 789
        assert config.ranker_role_id == 111
        assert config.reminders_sent == {"ABC:submit"}


class TestConfigStoreGetConfig:
    """Tests for ConfigStore.get_config."""

    def test_returns_empty_config_for_new_server(self, store):
        config = store.get_config(999)
        assert config.server_id == 999
        assert config.tracked_games == set()

    def test_returns_same_config_on_repeated_calls(self, store):
        config1 = store.get_config(999)
        config2 = store.get_config(999)
        assert config1 is config2


class TestConfigStoreTrackUntrack:
    """Tests for track_game and untrack_game."""

    def test_track_new_game_returns_true(self, store):
        assert store.track_game(1, "GAME1") is True

    def test_track_duplicate_game_returns_false(self, store):
        store.track_game(1, "GAME1")
        assert store.track_game(1, "GAME1") is False

    def test_tracked_game_appears_in_config(self, store):
        store.track_game(1, "GAME1")
        config = store.get_config(1)
        assert "GAME1" in config.tracked_games

    def test_untrack_existing_game_returns_true(self, store):
        store.track_game(1, "GAME1")
        assert store.untrack_game(1, "GAME1") is True

    def test_untrack_nonexistent_game_returns_false(self, store):
        assert store.untrack_game(1, "GAME1") is False

    def test_untracked_game_removed_from_config(self, store):
        store.track_game(1, "GAME1")
        store.untrack_game(1, "GAME1")
        config = store.get_config(1)
        assert "GAME1" not in config.tracked_games

    def test_track_multiple_games(self, store):
        store.track_game(1, "GAME1")
        store.track_game(1, "GAME2")
        store.track_game(1, "GAME3")
        config = store.get_config(1)
        assert config.tracked_games == {"GAME1", "GAME2", "GAME3"}


class TestConfigStoreChannelRole:
    """Tests for set_channel and set_role."""

    def test_set_channel(self, store):
        store.set_channel(1, 12345)
        assert store.get_config(1).notification_channel_id == 12345

    def test_set_role(self, store):
        store.set_role(1, 67890)
        assert store.get_config(1).ranker_role_id == 67890

    def test_set_channel_overwrites(self, store):
        store.set_channel(1, 111)
        store.set_channel(1, 222)
        assert store.get_config(1).notification_channel_id == 222


class TestConfigStoreReminders:
    """Tests for reminder deduplication."""

    def test_mark_and_check_reminder(self, store):
        store.mark_reminder_sent(1, "GAME1", "submit")
        assert store.is_reminder_sent(1, "GAME1", "submit") is True

    def test_reminder_not_sent_initially(self, store):
        assert store.is_reminder_sent(1, "GAME1", "submit") is False

    def test_different_deadline_types_independent(self, store):
        store.mark_reminder_sent(1, "GAME1", "submit")
        assert store.is_reminder_sent(1, "GAME1", "rank") is False

    def test_different_games_independent(self, store):
        store.mark_reminder_sent(1, "GAME1", "submit")
        assert store.is_reminder_sent(1, "GAME2", "submit") is False


class TestConfigStoreGetServersTracking:
    """Tests for get_servers_tracking."""

    def test_returns_empty_when_no_servers_track(self, store):
        assert store.get_servers_tracking("GAME1") == []

    def test_returns_servers_tracking_game(self, store):
        store.track_game(1, "GAME1")
        store.track_game(2, "GAME1")
        store.track_game(3, "OTHER")
        results = store.get_servers_tracking("GAME1")
        server_ids = {c.server_id for c in results}
        assert server_ids == {1, 2}

    def test_does_not_include_servers_not_tracking(self, store):
        store.track_game(1, "GAME1")
        store.track_game(2, "GAME2")
        results = store.get_servers_tracking("GAME1")
        assert len(results) == 1
        assert results[0].server_id == 1


class TestConfigStorePersistence:
    """Tests for save and load."""

    def test_save_creates_file(self, store, tmp_path):
        store.track_game(1, "GAME1")
        store.save()
        config_path = tmp_path / "config.json"
        assert config_path.exists()

    def test_save_creates_parent_directories(self, tmp_path):
        nested_path = tmp_path / "deep" / "nested" / "config.json"
        s = ConfigStore(path=str(nested_path))
        s.track_game(1, "GAME1")
        s.save()
        assert nested_path.exists()

    def test_load_restores_state(self, tmp_path):
        config_path = tmp_path / "config.json"
        s1 = ConfigStore(path=str(config_path))
        s1.track_game(1, "GAME1")
        s1.track_game(1, "GAME2")
        s1.set_channel(1, 999)
        s1.set_role(1, 888)
        s1.mark_reminder_sent(1, "GAME1", "submit")
        s1.save()

        s2 = ConfigStore(path=str(config_path))
        s2.load()
        config = s2.get_config(1)
        assert config.tracked_games == {"GAME1", "GAME2"}
        assert config.notification_channel_id == 999
        assert config.ranker_role_id == 888
        assert "GAME1:submit" in config.reminders_sent

    def test_load_nonexistent_file_does_nothing(self, tmp_path):
        config_path = tmp_path / "missing.json"
        s = ConfigStore(path=str(config_path))
        s.load()  # Should not raise
        assert s.get_servers_tracking("anything") == []

    def test_json_format(self, store, tmp_path):
        store.track_game(123, "ABC")
        store.set_channel(123, 456)
        store.set_role(123, 789)
        store.mark_reminder_sent(123, "ABC", "submit")
        store.save()

        config_path = tmp_path / "config.json"
        with open(config_path) as f:
            data = json.load(f)

        assert "servers" in data
        assert "123" in data["servers"]
        server = data["servers"]["123"]
        assert server["server_id"] == 123
        assert server["tracked_games"] == ["ABC"]
        assert server["notification_channel_id"] == 456
        assert server["ranker_role_id"] == 789
        assert server["reminders_sent"] == ["ABC:submit"]

    def test_round_trip_multiple_servers(self, tmp_path):
        config_path = tmp_path / "config.json"
        s1 = ConfigStore(path=str(config_path))
        s1.track_game(1, "A")
        s1.track_game(2, "B")
        s1.track_game(2, "C")
        s1.set_channel(1, 100)
        s1.set_channel(2, 200)
        s1.save()

        s2 = ConfigStore(path=str(config_path))
        s2.load()
        assert s2.get_config(1).tracked_games == {"A"}
        assert s2.get_config(2).tracked_games == {"B", "C"}
        assert s2.get_config(1).notification_channel_id == 100
        assert s2.get_config(2).notification_channel_id == 200
