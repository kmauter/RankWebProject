"""Server configuration persistence store for the Discord bot.

Manages per-server tracking configuration (tracked games, notification channel,
Ranker role, and reminder deduplication) persisted to a JSON file.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ServerConfig:
    """Per-server tracking configuration."""

    server_id: int
    tracked_games: set[str] = field(default_factory=set)
    notification_channel_id: int | None = None
    ranker_role_id: int | None = None
    reminders_sent: set[str] = field(default_factory=set)


class ConfigStore:
    """Manages per-server tracking configuration persisted to JSON."""

    def __init__(self, path: str | None = None) -> None:
        if path is None:
            path = os.path.join(
                os.path.dirname(__file__), "data", "config.json"
            )
        self._path = Path(path)
        self._configs: dict[int, ServerConfig] = {}

    def get_config(self, server_id: int) -> ServerConfig:
        """Return the config for a server, creating an empty one if needed."""
        if server_id not in self._configs:
            self._configs[server_id] = ServerConfig(server_id=server_id)
        return self._configs[server_id]

    def track_game(self, server_id: int, game_code: str) -> bool:
        """Add a game to a server's tracked list.

        Returns True if the game was newly added, False if already tracked.
        """
        config = self.get_config(server_id)
        if game_code in config.tracked_games:
            return False
        config.tracked_games.add(game_code)
        return True

    def untrack_game(self, server_id: int, game_code: str) -> bool:
        """Remove a game from a server's tracked list.

        Returns True if the game was removed, False if it wasn't tracked.
        """
        config = self.get_config(server_id)
        if game_code not in config.tracked_games:
            return False
        config.tracked_games.discard(game_code)
        return True

    def set_channel(self, server_id: int, channel_id: int) -> None:
        """Set the notification channel for a server."""
        config = self.get_config(server_id)
        config.notification_channel_id = channel_id

    def set_role(self, server_id: int, role_id: int) -> None:
        """Set the Ranker role for a server."""
        config = self.get_config(server_id)
        config.ranker_role_id = role_id

    def mark_reminder_sent(
        self, server_id: int, game_code: str, deadline_type: str
    ) -> None:
        """Mark a reminder as sent for deduplication."""
        config = self.get_config(server_id)
        key = f"{game_code}:{deadline_type}"
        config.reminders_sent.add(key)

    def is_reminder_sent(
        self, server_id: int, game_code: str, deadline_type: str
    ) -> bool:
        """Check if a reminder has already been sent."""
        config = self.get_config(server_id)
        key = f"{game_code}:{deadline_type}"
        return key in config.reminders_sent

    def get_servers_tracking(self, game_code: str) -> list[ServerConfig]:
        """Return all ServerConfigs that track the given game_code."""
        return [
            config
            for config in self._configs.values()
            if game_code in config.tracked_games
        ]

    def save(self) -> None:
        """Persist current state to the JSON file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)

        data: dict = {"servers": {}}
        for server_id, config in self._configs.items():
            data["servers"][str(server_id)] = {
                "server_id": config.server_id,
                "tracked_games": sorted(config.tracked_games),
                "notification_channel_id": config.notification_channel_id,
                "ranker_role_id": config.ranker_role_id,
                "reminders_sent": sorted(config.reminders_sent),
            }

        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load state from the JSON file. Does nothing if file doesn't exist."""
        if not self._path.exists():
            return

        with open(self._path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._configs.clear()
        for _server_id_str, server_data in data.get("servers", {}).items():
            server_id = int(server_data["server_id"])
            config = ServerConfig(
                server_id=server_id,
                tracked_games=set(server_data.get("tracked_games", [])),
                notification_channel_id=server_data.get(
                    "notification_channel_id"
                ),
                ranker_role_id=server_data.get("ranker_role_id"),
                reminders_sent=set(server_data.get("reminders_sent", [])),
            )
            self._configs[server_id] = config
