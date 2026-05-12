from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

db = SQLAlchemy(app)
migrate = Migrate(app, db)
limiter = Limiter(get_remote_address, app=app, default_limits=[])

from app import routes as routes, models as models  # noqa: E402 — must import after db init
from app.tasks import start_scheduler  # noqa: E402

# Don't start the scheduler during tests.
# In production with Gunicorn, use --preload flag or run scheduler as a separate process
# to avoid multiple scheduler instances across workers.
if not app.config.get("TESTING"):
    start_scheduler()
