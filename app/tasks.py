import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db
from app.models import Game, Stage, Rank, Song, SongStat
from datetime import datetime, timezone
import random
import requests
from app.spotifyactions import create_spotify_playlist_for_game
from app.youtubeactions import create_youtube_playlist_for_game
from statistics import mean, median
from collections import defaultdict

logger = logging.getLogger(__name__)


def notify_bot_stage_transition(game_code: str, new_stage: str) -> None:
    """POST to the Discord bot's /notify endpoint when a game stage transition occurs.

    Handles connection errors gracefully — logs and continues so the scheduler
    is never disrupted if the bot is unreachable.
    """
    notify_url = app.config.get("BOT_NOTIFY_URL")
    notify_secret = app.config.get("BOT_NOTIFY_SECRET")

    if not notify_url or not notify_secret:
        logger.debug("BOT_NOTIFY_URL or BOT_NOTIFY_SECRET not configured; skipping bot notification.")
        return

    payload = {
        "game_code": game_code,
        "new_stage": new_stage,
        "secret": notify_secret,
    }

    try:
        resp = requests.post(notify_url, json=payload, timeout=5)
        if resp.ok:
            logger.info(f"Bot notified: game={game_code} new_stage={new_stage}")
        else:
            logger.warning(
                f"Bot notification returned {resp.status_code} for game={game_code}: {resp.text[:200]}"
            )
    except requests.RequestException as exc:
        logger.warning(f"Failed to notify bot for game={game_code}: {exc}")


def update_game_stages():
    with app.app_context():
        today = datetime.now(timezone.utc).date()

        # ROLL GAMES OVER FROM RANK TO DONE STAGE
        games = Game.query.filter(
            Game.stage == Stage.RANK,
            Game.rank_duedate <= today
        ).all()
        for game in games:
            db.session.add(game)

            # for each game, gather all rankings related to that game
            ranks = Rank.query.filter_by(game_id=game.id).all()

            # for each user in the game construct their ranking,
            # removing the songs they submitted from their ranking
            user_ranks = defaultdict(list)
            for rank in ranks:
                user_ranks[rank.user_id].append(rank)

            song_ranks = {}
            for user_id, user_rank_list in user_ranks.items():
                valid_ranks = []
                for rank in sorted(user_rank_list, key=lambda r: r.rank_position):
                    song = Song.query.get(rank.song_id)
                    if not song or song.user_id == user_id:
                        continue
                    valid_ranks.append(rank.song_id)

                for i, song_id in enumerate(valid_ranks, start=1):
                    song_ranks.setdefault(song_id, []).append(i)

            # calculate statistics for the game
            for song_id, positions in song_ranks.items():
                if not positions:
                    continue

                avg_rank = mean(positions)
                med_rank = median(positions)
                rank_range = max(positions) - min(positions) if len(positions) > 1 else 0
                controversy = sum(abs(p - avg_rank) for p in positions) / len(positions)

                stat = SongStat.query.filter_by(song_id=song_id, game_id=game.id).first()
                if not stat:
                    stat = SongStat(song_id=song_id, game_id=game.id)

                stat.avg_rank = avg_rank
                stat.median_rank = med_rank
                stat.rank_range = rank_range
                stat.controversy = controversy
                db.session.add(stat)

            game.stage = Stage.DONE

            db.session.commit()
            logger.info(f"Game {game.id} rolled over to finished stage.")
            notify_bot_stage_transition(game.game_code, "results")

        # ROLL GAMES OVER FROM SUBMIT TO RANK STAGE
        games = Game.query.filter(
            Game.stage == Stage.SUBMIT,
            Game.submission_duedate <= today
        ).all()
        for game in games:
            db.session.add(game)

            # Change the stage to RANK
            game.stage = Stage.RANK

            # Fetch all songs for the game
            songs = list(game.songs)
            random.shuffle(songs)
            game.song_order = [song.id for song in songs]

            if not songs:
                logger.info(f"No songs found for game {game.id}. Skipping playlist creation.")

            else:
                owner = game.owner
                spotify_refresh_token = owner.spotify_refresh_token if owner else None
                youtube_refresh_token = owner.youtube_refresh_token if owner else None

                if not spotify_refresh_token:
                    logger.info(f"Owner of game {game.id} has not connected Spotify. Skipping.")
                else:
                    spotify_url = create_spotify_playlist_for_game(
                        game,
                        songs,
                        f"{game.theme} ({game.game_code})",
                        spotify_refresh_token
                    )
                    game.spotify_playlist_url = spotify_url

                if not youtube_refresh_token:
                    logger.info(f"Owner of game {game.id} has not connected YouTube. Skipping.")
                else:
                    youtube_url = create_youtube_playlist_for_game(
                        game,
                        songs,
                        f"{game.theme} ({game.game_code})",
                        youtube_refresh_token
                    )
                    game.youtube_playlist_url = youtube_url

            db.session.commit()
            logger.info(f"Game {game.id} rolled over to ranking stage.")
            notify_bot_stage_transition(game.game_code, "rankings")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_game_stages, trigger="interval", hours=1)
    scheduler.start()
    logger.info("Scheduler started — running update_game_stages every hour.")
