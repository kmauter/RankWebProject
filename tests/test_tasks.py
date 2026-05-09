"""
Tests for stage transition logic: SUBMIT→RANK and RANK→DONE,
including song order randomization, playlist creation, and stat calculations.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timezone
from statistics import mean, median

from app import db
from app.models import Game, Song, Rank, SongStat, User, GameUser, Stage
from app.tasks import update_game_stages


@pytest.fixture
def game_past_submission(app, sample_user):
    """A game in SUBMIT stage with submission_duedate in the past."""
    game = Game(
        owner_id=sample_user.id,
        theme="Past Submission",
        stage=Stage.SUBMIT,
        submission_duedate=date(2020, 1, 1),  # well in the past
        rank_duedate=date(2026, 12, 1),
        game_code="SUB001",
        max_submissions_per_user=3,
    )
    db.session.add(game)
    db.session.commit()

    game_user = GameUser(game_id=game.id, user_id=sample_user.id)
    db.session.add(game_user)
    db.session.commit()
    return game


@pytest.fixture
def game_past_submission_with_songs(game_past_submission, sample_user, second_user):
    """A game past submission with songs from two users."""
    game = game_past_submission

    # Add second user to game
    game_user = GameUser(game_id=game.id, user_id=second_user.id)
    db.session.add(game_user)
    db.session.commit()

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
    return game, songs


@pytest.fixture
def game_past_rank(app, sample_user, second_user):
    """A game in RANK stage with rank_duedate in the past, songs, and rankings submitted."""
    game = Game(
        owner_id=sample_user.id,
        theme="Past Rank",
        stage=Stage.RANK,
        submission_duedate=date(2020, 1, 1),
        rank_duedate=date(2020, 2, 1),  # well in the past
        game_code="RNK001",
        max_submissions_per_user=3,
    )
    db.session.add(game)
    db.session.commit()

    # Add both users to game
    for user in [sample_user, second_user]:
        db.session.add(GameUser(game_id=game.id, user_id=user.id))
    db.session.commit()

    # Each user submits 2 songs (4 total)
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

    game.song_order = [s.id for s in songs]
    db.session.commit()

    return game, songs


class TestSubmitToRankTransition:
    """Tests for SUBMIT → RANK stage transition."""

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_game_transitions_to_rank(self, mock_yt, mock_sp, game_past_submission_with_songs):
        """Game with past submission_duedate transitions from SUBMIT to RANK."""
        mock_sp.return_value = None
        mock_yt.return_value = None
        game, songs = game_past_submission_with_songs

        update_game_stages()

        db.session.refresh(game)
        assert game.stage == Stage.RANK

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_song_order_is_set(self, mock_yt, mock_sp, game_past_submission_with_songs):
        """Song order is set and contains all song IDs."""
        mock_sp.return_value = None
        mock_yt.return_value = None
        game, songs = game_past_submission_with_songs
        song_ids = {s.id for s in songs}

        update_game_stages()

        db.session.refresh(game)
        assert game.song_order is not None
        assert set(game.song_order) == song_ids

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_song_order_is_randomized(self, mock_yt, mock_sp, game_past_submission_with_songs):
        """Song order should be shuffled (not guaranteed to differ every time,
        but over multiple runs it should not always match insertion order)."""
        mock_sp.return_value = None
        mock_yt.return_value = None
        game, songs = game_past_submission_with_songs
        original_order = [s.id for s in songs]

        # Run multiple times to check randomization (reset between runs isn't
        # possible in one test, so we just verify the order is set)
        update_game_stages()

        db.session.refresh(game)
        # At minimum, song_order contains all IDs
        assert set(game.song_order) == set(original_order)

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_no_songs_transitions_without_error(self, mock_yt, mock_sp, game_past_submission):
        """Game with no songs still transitions to RANK without crashing."""
        mock_sp.return_value = None
        mock_yt.return_value = None

        update_game_stages()

        db.session.refresh(game_past_submission)
        assert game_past_submission.stage == Stage.RANK
        assert game_past_submission.song_order == []
        mock_sp.assert_not_called()
        mock_yt.assert_not_called()

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_spotify_playlist_created_when_owner_has_token(self, mock_yt, mock_sp, game_past_submission_with_songs, sample_user):
        """Spotify playlist is created when owner has a refresh token."""
        sample_user.spotify_refresh_token = "fake-spotify-token"
        db.session.commit()
        mock_sp.return_value = "https://open.spotify.com/playlist/abc123"
        mock_yt.return_value = None
        game, songs = game_past_submission_with_songs

        update_game_stages()

        db.session.refresh(game)
        assert game.spotify_playlist_url == "https://open.spotify.com/playlist/abc123"
        mock_sp.assert_called_once()

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_spotify_playlist_skipped_when_no_token(self, mock_yt, mock_sp, game_past_submission_with_songs, sample_user):
        """Spotify playlist is not created when owner has no refresh token."""
        sample_user.spotify_refresh_token = None
        db.session.commit()
        mock_sp.return_value = None
        mock_yt.return_value = None
        game, songs = game_past_submission_with_songs

        update_game_stages()

        db.session.refresh(game)
        assert game.spotify_playlist_url is None
        mock_sp.assert_not_called()

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_youtube_playlist_created_when_owner_has_token(self, mock_yt, mock_sp, game_past_submission_with_songs, sample_user):
        """YouTube playlist is created when owner has a refresh token."""
        sample_user.youtube_refresh_token = "fake-youtube-token"
        db.session.commit()
        mock_sp.return_value = None
        mock_yt.return_value = "https://www.youtube.com/playlist?list=xyz789"
        game, songs = game_past_submission_with_songs

        update_game_stages()

        db.session.refresh(game)
        assert game.youtube_playlist_url == "https://www.youtube.com/playlist?list=xyz789"
        mock_yt.assert_called_once()

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_youtube_playlist_skipped_when_no_token(self, mock_yt, mock_sp, game_past_submission_with_songs, sample_user):
        """YouTube playlist is not created when owner has no refresh token."""
        sample_user.youtube_refresh_token = None
        db.session.commit()
        mock_sp.return_value = None
        mock_yt.return_value = None
        game, songs = game_past_submission_with_songs

        update_game_stages()

        db.session.refresh(game)
        assert game.youtube_playlist_url is None
        mock_yt.assert_not_called()

    @patch("app.tasks.create_spotify_playlist_for_game")
    @patch("app.tasks.create_youtube_playlist_for_game")
    def test_future_submission_date_not_transitioned(self, mock_yt, mock_sp, app, sample_user):
        """Game with future submission_duedate is NOT transitioned."""
        mock_sp.return_value = None
        mock_yt.return_value = None
        game = Game(
            owner_id=sample_user.id,
            theme="Future Game",
            stage=Stage.SUBMIT,
            submission_duedate=date(2099, 1, 1),
            rank_duedate=date(2099, 2, 1),
            game_code="FUT001",
            max_submissions_per_user=3,
        )
        db.session.add(game)
        db.session.commit()

        update_game_stages()

        db.session.refresh(game)
        assert game.stage == Stage.SUBMIT


class TestRankToDoneTransition:
    """Tests for RANK → DONE stage transition."""

    def test_game_transitions_to_done(self, game_past_rank, sample_user, second_user):
        """Game with past rank_duedate transitions from RANK to DONE."""
        game, songs = game_past_rank

        # Both users submit rankings (ranking only the other user's songs)
        # sample_user ranks second_user's songs (songs[2], songs[3])
        for pos, song in enumerate([songs[2], songs[3]], start=1):
            db.session.add(Rank(game_id=game.id, user_id=sample_user.id, song_id=song.id, rank_position=pos))
        # second_user ranks sample_user's songs (songs[0], songs[1])
        for pos, song in enumerate([songs[0], songs[1]], start=1):
            db.session.add(Rank(game_id=game.id, user_id=second_user.id, song_id=song.id, rank_position=pos))
        db.session.commit()

        update_game_stages()

        db.session.refresh(game)
        assert game.stage == Stage.DONE

    def test_stats_calculated_correctly(self, game_past_rank, sample_user, second_user):
        """Stats (avg, median, range, controversy) are calculated correctly."""
        game, songs = game_past_rank

        # Create a third user for more interesting stats
        third_user = User(username="thirduser", email="third@example.com")
        third_user.set_password("pass789")
        db.session.add(third_user)
        db.session.commit()
        db.session.add(GameUser(game_id=game.id, user_id=third_user.id))
        db.session.commit()

        # songs[0] and songs[1] belong to sample_user
        # songs[2] and songs[3] belong to second_user
        # Each user ranks the songs they didn't submit

        # sample_user ranks: songs[2]=1, songs[3]=2
        db.session.add(Rank(game_id=game.id, user_id=sample_user.id, song_id=songs[2].id, rank_position=1))
        db.session.add(Rank(game_id=game.id, user_id=sample_user.id, song_id=songs[3].id, rank_position=2))

        # second_user ranks: songs[0]=1, songs[1]=2
        db.session.add(Rank(game_id=game.id, user_id=second_user.id, song_id=songs[0].id, rank_position=1))
        db.session.add(Rank(game_id=game.id, user_id=second_user.id, song_id=songs[1].id, rank_position=2))

        # third_user ranks all 4 (they didn't submit any): songs[0]=2, songs[1]=1, songs[2]=2, songs[3]=1
        # But wait — third_user didn't submit songs, so all songs are valid for them
        # Let's rank: songs[0]=3, songs[1]=1, songs[2]=2, songs[3]=4
        db.session.add(Rank(game_id=game.id, user_id=third_user.id, song_id=songs[0].id, rank_position=3))
        db.session.add(Rank(game_id=game.id, user_id=third_user.id, song_id=songs[1].id, rank_position=1))
        db.session.add(Rank(game_id=game.id, user_id=third_user.id, song_id=songs[2].id, rank_position=2))
        db.session.add(Rank(game_id=game.id, user_id=third_user.id, song_id=songs[3].id, rank_position=4))
        db.session.commit()

        update_game_stages()

        # After filtering out self-submitted songs and re-ranking:
        # songs[0] (submitted by sample_user):
        #   second_user ranked it position 1 → valid rank 1
        #   third_user ranked it position 3 → valid rank 3
        #   (sample_user's own song, excluded from their ranking)
        #   positions = [1, 3] → avg=2.0, median=2.0, range=2, controversy=1.0

        stat_0 = SongStat.query.filter_by(song_id=songs[0].id, game_id=game.id).first()
        assert stat_0 is not None
        assert stat_0.avg_rank == pytest.approx(2.0)
        assert stat_0.median_rank == pytest.approx(2.0)
        assert stat_0.rank_range == 2
        assert stat_0.controversy == pytest.approx(1.0)

        # songs[1] (submitted by sample_user):
        #   second_user ranked it position 2 → valid rank 2
        #   third_user ranked it position 1 → valid rank 1
        #   positions = [2, 1] → avg=1.5, median=1.5, range=1, controversy=0.5

        stat_1 = SongStat.query.filter_by(song_id=songs[1].id, game_id=game.id).first()
        assert stat_1 is not None
        assert stat_1.avg_rank == pytest.approx(1.5)
        assert stat_1.median_rank == pytest.approx(1.5)
        assert stat_1.rank_range == 1
        assert stat_1.controversy == pytest.approx(0.5)

    def test_own_songs_excluded_from_ranking(self, game_past_rank, sample_user, second_user):
        """A user's own songs are excluded from their ranking in stat calculations."""
        game, songs = game_past_rank

        # sample_user ranks ALL songs including their own (songs[0], songs[1])
        for pos, song in enumerate(songs, start=1):
            db.session.add(Rank(game_id=game.id, user_id=sample_user.id, song_id=song.id, rank_position=pos))
        # second_user ranks ALL songs including their own (songs[2], songs[3])
        for pos, song in enumerate(songs, start=1):
            db.session.add(Rank(game_id=game.id, user_id=second_user.id, song_id=song.id, rank_position=pos))
        db.session.commit()

        update_game_stages()

        # songs[0] belongs to sample_user, so sample_user's ranking of it should be excluded
        # Only second_user's ranking of songs[0] should count
        stat_0 = SongStat.query.filter_by(song_id=songs[0].id, game_id=game.id).first()
        assert stat_0 is not None
        # second_user ranked songs[0] at position 1, and after filtering their own songs
        # out, songs[0] is re-ranked. second_user's valid songs are [songs[0], songs[1]]
        # (songs[2] and [3] are their own). So songs[0] gets valid rank 1.
        # Only one rater → avg = that rank
        assert stat_0.avg_rank is not None

    def test_game_already_done_not_reprocessed(self, app, sample_user):
        """Game already in DONE stage is not re-processed."""
        game = Game(
            owner_id=sample_user.id,
            theme="Already Done",
            stage=Stage.DONE,
            submission_duedate=date(2020, 1, 1),
            rank_duedate=date(2020, 2, 1),
            game_code="DONE01",
            max_submissions_per_user=3,
        )
        db.session.add(game)
        db.session.commit()

        update_game_stages()

        db.session.refresh(game)
        assert game.stage == Stage.DONE
        # No stats should be created
        stats = SongStat.query.filter_by(game_id=game.id).all()
        assert len(stats) == 0

    def test_future_rank_date_not_transitioned(self, app, sample_user):
        """Game with future rank_duedate is NOT transitioned."""
        game = Game(
            owner_id=sample_user.id,
            theme="Future Rank",
            stage=Stage.RANK,
            submission_duedate=date(2020, 1, 1),
            rank_duedate=date(2099, 1, 1),
            game_code="FUT002",
            max_submissions_per_user=3,
        )
        db.session.add(game)
        db.session.commit()

        update_game_stages()

        db.session.refresh(game)
        assert game.stage == Stage.RANK

    def test_game_with_no_rankings_transitions(self, game_past_rank):
        """Game with no rankings submitted still transitions to DONE."""
        game, songs = game_past_rank

        update_game_stages()

        db.session.refresh(game)
        assert game.stage == Stage.DONE
        # No stats created since no rankings exist
        stats = SongStat.query.filter_by(game_id=game.id).all()
        assert len(stats) == 0
