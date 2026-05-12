"""
Tests for song submission endpoints: submit, get, delete.
"""
import pytest
from tests.conftest import make_auth_header
from app.models import Song, Stage, Game
from app import db


class TestSubmitSong:
    """Tests for POST /api/submit-song"""

    def test_submit_song_valid(self, client, sample_game, sample_user):
        """Submit a song during submission stage succeeds."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "Imagine",
            "artist": "John Lennon",
            "comment": "Classic",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["song"]["song_name"] == "Imagine"
        assert data["song"]["artist"] == "John Lennon"

    def test_submit_song_during_ranking_stage(self, client, sample_game, sample_user):
        """Submit song when game is in RANK stage returns 400."""
        sample_game.stage = Stage.RANK
        db.session.commit()

        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "Hey Jude",
            "artist": "The Beatles",
        })
        assert resp.status_code == 400
        assert "not in the submission stage" in resp.get_json()["error"]

    def test_submit_song_as_non_member(self, client, sample_game, second_user):
        """Non-member cannot submit songs."""
        headers = make_auth_header(second_user.id)
        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "Hey Jude",
            "artist": "The Beatles",
        })
        assert resp.status_code == 403
        assert "not part of the game" in resp.get_json()["error"]

    def test_submit_duplicate_song(self, client, sample_game, sample_user):
        """Submitting the same song twice returns 400."""
        headers = make_auth_header(sample_user.id)
        payload = {
            "game_code": "TEST01",
            "song_name": "Imagine",
            "artist": "John Lennon",
        }
        client.post("/api/submit-song", headers=headers, json=payload)
        resp = client.post("/api/submit-song", headers=headers, json=payload)
        assert resp.status_code == 400
        assert "already submitted" in resp.get_json()["error"]

    def test_submit_exceeds_max_limit(self, client, sample_game, sample_user):
        """Submitting more than max_submissions_per_user returns 400."""
        headers = make_auth_header(sample_user.id)
        # max is 3 for sample_game
        for i in range(3):
            client.post("/api/submit-song", headers=headers, json={
                "game_code": "TEST01",
                "song_name": f"Song {i}",
                "artist": f"Artist {i}",
            })

        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "One Too Many",
            "artist": "Overflow",
        })
        assert resp.status_code == 400
        assert "Maximum" in resp.get_json()["error"]

    def test_submit_at_limit_minus_one(self, client, sample_game, sample_user):
        """Submitting at max-1 still succeeds."""
        headers = make_auth_header(sample_user.id)
        # Submit 2 songs (max is 3)
        for i in range(2):
            client.post("/api/submit-song", headers=headers, json={
                "game_code": "TEST01",
                "song_name": f"Song {i}",
                "artist": f"Artist {i}",
            })

        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "Third Song",
            "artist": "Third Artist",
        })
        assert resp.status_code == 201

    def test_submit_missing_title(self, client, sample_game, sample_user):
        """Submit without title returns 400."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "artist": "Someone",
        })
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json()["error"]

    def test_submit_missing_artist(self, client, sample_game, sample_user):
        """Submit without artist returns 400."""
        headers = make_auth_header(sample_user.id)
        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "Something",
        })
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json()["error"]


class TestGetMySongs:
    """Tests for GET /api/my-game-songs"""

    def test_get_my_songs(self, client, sample_game, sample_user):
        """Returns only the current user's songs."""
        headers = make_auth_header(sample_user.id)
        # Submit a song first
        client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "My Song",
            "artist": "Me",
        })

        resp = client.get("/api/my-game-songs?game_code=TEST01", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["song_name"] == "My Song"

    def test_get_my_songs_non_member(self, client, sample_game, second_user):
        """Non-member gets 403."""
        headers = make_auth_header(second_user.id)
        resp = client.get("/api/my-game-songs?game_code=TEST01", headers=headers)
        assert resp.status_code == 403


class TestGetAllGameSongs:
    """Tests for GET /api/game/<game_code>/songs"""

    def test_get_all_songs_as_member(self, client, sample_game_with_players, sample_user, second_user):
        """Member can see all songs in the game."""
        # Submit songs from both users
        h1 = make_auth_header(sample_user.id)
        h2 = make_auth_header(second_user.id)
        client.post("/api/submit-song", headers=h1, json={
            "game_code": "TEST01",
            "song_name": "Song A",
            "artist": "Artist A",
        })
        client.post("/api/submit-song", headers=h2, json={
            "game_code": "TEST01",
            "song_name": "Song B",
            "artist": "Artist B",
        })

        resp = client.get("/api/game/TEST01/songs", headers=h1)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2

    def test_get_all_songs_as_non_member(self, client, sample_game, second_user):
        """Non-member gets 403."""
        headers = make_auth_header(second_user.id)
        resp = client.get("/api/game/TEST01/songs", headers=headers)
        assert resp.status_code == 403


class TestDeleteSong:
    """Tests for DELETE /api/song/<song_id>"""

    def test_delete_song_as_owner(self, client, sample_game_with_players, sample_user, second_user):
        """Game owner can delete any song (including other users' songs)."""
        # Second user submits a song
        h2 = make_auth_header(second_user.id)
        resp = client.post("/api/submit-song", headers=h2, json={
            "game_code": "TEST01",
            "song_name": "Their Song",
            "artist": "Second User",
        })
        song_id = resp.get_json()["song"]["id"]

        # Owner deletes it
        h1 = make_auth_header(sample_user.id)
        resp = client.delete(f"/api/song/{song_id}", headers=h1)
        assert resp.status_code == 200
        assert Song.query.get(song_id) is None

    def test_delete_own_song(self, client, sample_game_with_players, second_user):
        """A user can delete their own song submission."""
        headers = make_auth_header(second_user.id)
        resp = client.post("/api/submit-song", headers=headers, json={
            "game_code": "TEST01",
            "song_name": "My Song",
            "artist": "Me",
        })
        song_id = resp.get_json()["song"]["id"]

        resp = client.delete(f"/api/song/{song_id}", headers=headers)
        assert resp.status_code == 200
        assert Song.query.get(song_id) is None

    def test_delete_other_users_song_as_non_owner(self, client, sample_game_with_players, sample_user, second_user):
        """Non-owner cannot delete another user's song."""
        # Owner submits a song
        h1 = make_auth_header(sample_user.id)
        resp = client.post("/api/submit-song", headers=h1, json={
            "game_code": "TEST01",
            "song_name": "Protected",
            "artist": "Safe",
        })
        song_id = resp.get_json()["song"]["id"]

        # Second user (non-owner) tries to delete owner's song
        h2 = make_auth_header(second_user.id)
        resp = client.delete(f"/api/song/{song_id}", headers=h2)
        assert resp.status_code == 403

    def test_delete_nonexistent_song(self, client, sample_user):
        """Deleting non-existent song returns 404."""
        headers = make_auth_header(sample_user.id)
        resp = client.delete("/api/song/9999", headers=headers)
        assert resp.status_code == 404
