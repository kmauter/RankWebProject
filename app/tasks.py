from apscheduler.schedulers.background import BackgroundScheduler
from app import app, db
from app.models import Game, Stage
from datetime import datetime, timezone

def update_game_stages():
    with app.app_context():
        now = datetime.now(timezone.utc)
        games = Game.query.filter(
            Game.stage == Stage.SUBMIT,
            Game.submission_duedate <= now
        ).all()
        for game in games:
            game.stage = Stage.RANK
            db.session.add(game)
            db.session.commit()
            print(f"Game {game.id} rolled over to ranking stage.")
            
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_game_stages, trigger="interval", minutes=15)
    scheduler.start()
        