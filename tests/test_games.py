"""
Tests for game management endpoints: create, join, get details, update, players.
"""
import pytest
from tests.conftest import make_auth_header
from app.models import Game, GameUser, Stage
from app import db


class TestCreateGame:
    """Tests for POST /api/games"""

    def test_create_game_valid(self, client, sample_user):
        """Create game with valid data returns 201 and game code."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/games", headers=headers, json={
            "theme": "Best 90s Songs",
            "description": "Nostalgia trip",
            "submissionDuedate": "2026-06-01",
            "rankDuedate": "2026-06-15",
            "maxSubmissionsPerUser": 3,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "game_code" in data
        assert len(data["game_code"]) == 6

    def test_create_game_missing_theme(self, client, sample_user):
        """Create game without theme returns 400."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/games", headers=headers, json={
            "submissionDuedate": "2026-06-01",
            "rankDuedate": "2026-06-15",
        })
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json()["error"]

    def test_create_game_missing_dates(self, client, sample_user):
        """Create game without dates returns 400."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/games", headers=headers, json={
            "theme": "Test",
        })
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json()["error"]

    def test_create_game_invalid_date_format(self, client, sample_user):
        """Create game with bad date format returns 400."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/games", headers=headers, json={
            "theme": "Test",
            "submissionDuedate": "06/01/2026",
            "rankDuedate": "06/15/2026",
        })
        assert resp.status_code == 400
        assert "Invalid date format" in resp.get_json()["error"]

    def test_creator_added_as_player(self, client, sample_user):
        """Creator is automatically added as a player in the game."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/games", headers=headers, json={
            "theme": "Auto Join Test",
            "submissionDuedate": "2026-06-01",
            "rankDuedate": "2026-06-15",
        })
        game_code = resp.get_json()["game_code"]
        game = Game.query.filter_by(game_code=game_code).first()
        game_user = GameUser.query.filter_by(game_id=game.id, user_id=sample_user.id).first()
        assert game_user is not None


class TestJoinGame:
    """Tests for POST /api/join-game"""

    def test_join_valid_code(self, client, sample_game, second_user):
        """Join game with valid code succeeds."""
        headers = make_auth_header(second_user.id)
        resp = client.post("/api/join-game", headers=headers, json={
            "game_code": "TEST01",
        })
        assert resp.status_code == 200
        assert "User added to game successfully" in resp.get_json()["message"]

    def test_join_invalid_code(self, client, sample_user):
        """Join game with invalid code returns 404."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/join-game", headers=headers, json={
            "game_code": "ZZZZZ9",
        })
        assert resp.status_code == 404
        assert "Game not found" in resp.get_json()["error"]

    def test_join_already_joined(self, client, sample_game, sample_user):
        """Join game already joined returns 400."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/join-game", headers=headers, json={
            "game_code": "TEST01",
        })
        assert resp.status_code == 400
        assert "already part of the game" in resp.get_json()["error"]


class TestGetUserGames:
    """Tests for GET /api/user-games"""

    def test_get_user_games(self, client, sample_game, sample_user):
        """Returns all games the user is part of."""
        headers = make_auth_header(sample_user.id)
        resp = client.get("/api/user-games", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Theme"
        assert data[0]["gameCode"] == "TEST01"


class TestGetGameDetails:
    """Tests for GET /api/game/<game_code>"""

    def test_get_game_as_member(self, client, sample_game, sample_user):
        """Member can get game details."""
        headers = make_auth_header(sample_user.id)
        resp = client.get("/api/game/TEST01", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["title"] == "Test Theme"
        assert data["gameCode"] == "TEST01"

    def test_get_game_as_non_member(self, client, sample_game, second_user):
        """Non-member gets 403."""
        headers = make_auth_header(second_user.id)
        resp = client.get("/api/game/TEST01", headers=headers)
        assert resp.status_code == 403
        assert "not part of the game" in resp.get_json()["error"]


class TestUpdateGame:
    """Tests for PATCH /api/game/<game_code>/update-game"""

    def test_update_submission_date_as_owner(self, client, sample_game, sample_user):
        """Owner can update submission due date."""
        headers = make_auth_header(sample_user.id)
        resp = client.patch("/api/game/TEST01/update-game", headers=headers, json={
            "submissionDuedate": "2026-07-01",
        })
        assert resp.status_code == 200
        game = Game.query.filter_by(game_code="TEST01").first()
        assert str(game.submission_duedate) == "2026-07-01"

    def test_update_game_as_non_owner(self, client, sample_game_with_players, second_user):
        """Non-owner gets 403 when trying to update."""
        headers = make_auth_header(second_user.id)
        resp = client.patch("/api/game/TEST01/update-game", headers=headers, json={
            "submissionDuedate": "2026-07-01",
        })
        assert resp.status_code == 403
        assert "Only the game owner" in resp.get_json()["error"]


class TestGetPlayers:
    """Tests for GET /api/game/<game_code>/players"""

    def test_get_players(self, client, sample_game_with_players, sample_user):
        """Returns all players in the game."""
        headers = make_auth_header(sample_user.id)
        resp = client.get("/api/game/TEST01/players", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        usernames = [p["username"] for p in data]
        assert "testuser" in usernames
        assert "seconduser" in usernames


class TestRemovePlayer:
    """Tests for DELETE /api/game/<game_code>/player/<user_id>"""

    def test_remove_player_as_owner(self, client, sample_game_with_players, sample_user, second_user):
        """Owner can remove a player."""
        headers = make_auth_header(sample_user.id)
        resp = client.delete(f"/api/game/TEST01/player/{second_user.id}", headers=headers)
        assert resp.status_code == 200
        assert "Player removed" in resp.get_json()["message"]

    def test_remove_player_as_non_owner(self, client, sample_game_with_players, second_user, sample_user):
        """Non-owner gets 403."""
        headers = make_auth_header(second_user.id)
        resp = client.delete(f"/api/game/TEST01/player/{sample_user.id}", headers=headers)
        assert resp.status_code == 403

    def test_remove_nonexistent_player(self, client, sample_game, sample_user):
        """Removing a player not in the game returns 404."""
        headers = make_auth_header(sample_user.id)
        resp = client.delete("/api/game/TEST01/player/9999", headers=headers)
        assert resp.status_code == 404
