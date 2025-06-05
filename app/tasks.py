from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db
from app.models import Game, Stage
from datetime import datetime, timezone
import random
from app.spotifyactions import create_spotify_playlist_for_game
from app.youtubeactions import create_youtube_playlist_for_game

def update_game_stages():
    with app.app_context():
        now = datetime.now(timezone.utc)
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
    scheduler.add_job(func=update_game_stages, trigger="interval", minutes=15)
    scheduler.start()
        
# Automation Between
# - When submission due date is passed, trigger Automation
# - Randomize order of songs
# - Create Spotify playlist (if given spotify account to make playlist in)
# - Create Youtube playlist (if given youtube account to make playlist in OR default account)
# - Switch stage to ranking
# - Fetch additional song data from spotify (loudness, happiness, etc.)