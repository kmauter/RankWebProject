from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db
from app.models import Game, Stage, Rank, Song, SongStat
from datetime import datetime, timezone
import random
from app.spotifyactions import create_spotify_playlist_for_game
from app.youtubeactions import create_youtube_playlist_for_game
from statistics import mean, median
from collections import defaultdict

def update_game_stages():
    with app.app_context():
        now = datetime.now(timezone.utc)
        
        # ROLL GAMES OVER FROM RANK TO DONE STAGE 
        games = Game.query.filter(
            Game.stage == Stage.RANK,
            Game.rank_duedate <= now
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
            # # avg rank, median rank, range, controversy score, and user who submitted
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
            print(f"Game {game.id} rolled over to finished stage.")
        
        # ROLL GAMES OVER FROM SUBMIT TO RANK STAGE
        games = Game.query.filter(
            Game.stage == Stage.SUBMIT,
            Game.submission_duedate <= now
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
                print(f"No songs found for game {game.id}. Skipping playlist creation.")
            
            else:
                owner = game.owner
                spotify_refresh_token = owner.spotify_refresh_token if owner else None
                youtube_refresh_token = owner.youtube_refresh_token if owner else None
                
                if not spotify_refresh_token:
                    print(f"Owner of game {game.id} has not connected their Spotify. Skipping Spotify playlist creation.")
                else:
                    spotify_url = create_spotify_playlist_for_game(
                        game, 
                        songs, 
                        f"{game.theme} ({game.game_code})",
                        spotify_refresh_token
                    )
                    game.spotify_playlist_url = spotify_url
                    
                if not youtube_refresh_token:
                    print(f"Owner of game {game.id} has not connected their YouTube. Skipping YouTube playlist creation.")
                else:
                    youtube_url = create_youtube_playlist_for_game(
                        game, 
                        songs,
                        f"{game.theme} ({game.game_code})", 
                        youtube_refresh_token
                    )
                    game.youtube_playlist_url = youtube_url
                
            db.session.commit()
            print(f"Game {game.id} rolled over to ranking stage.")
            
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_game_stages, trigger="interval", hours=1)
    scheduler.start()
        
# Automation Between
# - When submission due date is passed, trigger Automation
# - Randomize order of songs
# - Create Spotify playlist (if given spotify account to make playlist in)
# - Create Youtube playlist (if given youtube account to make playlist in OR default account)
# - Switch stage to ranking
# - Fetch additional song data from spotify (loudness, happiness, etc.)