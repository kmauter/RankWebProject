"""
Tests for ranking endpoints: save, get, patch, delete rankings.
"""
import pytest
from tests.conftest import make_auth_header
from app.models import Song, Rank, Stage, Game, GameUser
from app import db


@pytest.fixture
def game_in_rank_stage(sample_game_with_players, sample_user, second_user):
    """A game in RANK stage with songs submitted by both users."""
    game = sample_game_with_players
    game.stage = Stage.RANK
    db.session.commit()

    # Add songs from both users
    songs = []
    for i, user in enumerate([sample_user, second_user]):
        for j in range(2):
            song = Song(
                game_id=game.id,
                user_id=user.id,
                title=f"Song {i*2 + j + 1}",
                artist=f"Artist {i*2 + j + 1}",
            )
            db.session.add(song)
            songs.append(song)
    db.session.commit()

    # Set song order
    game.song_order = [s.id for s in songs]
    db.session.commit()

    return game, songs


class TestSaveRankings:
    """Tests for POST /api/game/<game_code>/rankings"""

    def test_save_full_ranking(self, client, game_in_rank_stage, sample_user):
        """Save a complete ranking for all songs."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)
        ranking = [s.id for s in songs]

        resp = client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": ranking,
        })
        assert resp.status_code == 200
        assert "saved" in resp.get_json()["message"].lower()

        # Verify ranks stored
        ranks = Rank.query.filter_by(game_id=game.id, user_id=sample_user.id).all()
        assert len(ranks) == 4

    def test_save_partial_ranking_with_nulls(self, client, game_in_rank_stage, sample_user):
        """Save ranking with some null positions."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)
        ranking = [songs[0].id, None, songs[2].id, None]

        resp = client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": ranking,
        })
        assert resp.status_code == 200

        # Only non-null ranks stored
        ranks = Rank.query.filter_by(game_id=game.id, user_id=sample_user.id).all()
        assert len(ranks) == 2

    def test_save_ranking_replaces_previous(self, client, game_in_rank_stage, sample_user):
        """Saving a new ranking replaces the old one."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)

        # Save first ranking
        ranking1 = [s.id for s in songs]
        client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": ranking1,
        })

        # Save different ranking
        ranking2 = list(reversed([s.id for s in songs]))
        resp = client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": ranking2,
        })
        assert resp.status_code == 200

        # Verify new order
        ranks = Rank.query.filter_by(
            game_id=game.id, user_id=sample_user.id
        ).order_by(Rank.rank_position).all()
        assert [r.song_id for r in ranks] == ranking2

    def test_save_empty_ranking(self, client, game_in_rank_stage, sample_user):
        """Saving empty ranking returns 400."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)

        resp = client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": [],
        })
        assert resp.status_code == 400

    def test_multiple_users_rank_independently(self, client, game_in_rank_stage, sample_user, second_user):
        """Each user's ranking is isolated."""
        game, songs = game_in_rank_stage
        ranking_a = [s.id for s in songs]
        ranking_b = list(reversed([s.id for s in songs]))

        client.post(f"/api/game/{game.game_code}/rankings",
                    headers=make_auth_header(sample_user.id),
                    json={"ranking": ranking_a})
        client.post(f"/api/game/{game.game_code}/rankings",
                    headers=make_auth_header(second_user.id),
                    json={"ranking": ranking_b})

        ranks_a = Rank.query.filter_by(game_id=game.id, user_id=sample_user.id).order_by(Rank.rank_position).all()
        ranks_b = Rank.query.filter_by(game_id=game.id, user_id=second_user.id).order_by(Rank.rank_position).all()

        assert [r.song_id for r in ranks_a] == ranking_a
        assert [r.song_id for r in ranks_b] == ranking_b


class TestGetRankings:
    """Tests for GET /api/game/<game_code>/rankings"""

    def test_get_ranking_returns_correct_order(self, client, game_in_rank_stage, sample_user):
        """Get ranking returns the saved order."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)
        ranking = [s.id for s in songs]

        client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": ranking,
        })

        resp = client.get(f"/api/game/{game.game_code}/rankings", headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()["ranking"] == ranking

    def test_get_ranking_when_none_saved(self, client, game_in_rank_stage, sample_user):
        """Get ranking when nothing saved returns empty list."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)

        resp = client.get(f"/api/game/{game.game_code}/rankings", headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()["ranking"] == []


class TestDeleteRankings:
    """Tests for DELETE /api/game/<game_code>/rankings"""

    def test_delete_ranking(self, client, game_in_rank_stage, sample_user):
        """Delete removes all user ranks for the game."""
        game, songs = game_in_rank_stage
        headers = make_auth_header(sample_user.id)

        # Save then delete
        client.post(f"/api/game/{game.game_code}/rankings", headers=headers, json={
            "ranking": [s.id for s in songs],
        })
        resp = client.delete(f"/api/game/{game.game_code}/rankings", headers=headers)
        assert resp.status_code == 200

        ranks = Rank.query.filter_by(game_id=game.id, user_id=sample_user.id).all()
        assert len(ranks) == 0
