from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db
from app.models import Game, Stage
from datetime import datetime, timezone
import random
from app.spotifyactions import create_spotify_playlist_for_game
from app.youtubeactions import create_youtube_playlist

def update_game_stages():
    with app.app_context():
        now = datetime.now(timezone.utc)
        games = Game.query.filter(
            Game.stage == Stage.SUBMIT,
            Game.submission_duedate <= now
        ).all()
        for game in games:
            # Change the stage to RANK
            game.stage = Stage.RANK
            db.session.add(game)
            
            # Fetch all songs for the game
            songs = list(game.songs)
            
            # Randomize the order of the songs, then create playlists
            random.shuffle(songs)
            
            # Find spotify and youtube links for the game
            # they will not have them at this point, so we will need to find them
            spotify_url = create_spotify_playlist_for_game(game, songs, user_spotify_id="...")
            youtube_url = create_youtube_playlist(f"{game.theme}", f"Auto-generated playlist for {game.theme} ({game.game_code})", songs)

            game.spotify_playlist_url = spotify_url
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