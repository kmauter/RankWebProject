from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from app.config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
app.logger.setLevel(logging.INFO)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
CORS(app, origins=["https://rankwebgame.com", "http://localhost:3000"])

from app import routes as routes, models as models  # noqa: E402 — must import after db init
from app.tasks import start_scheduler  # noqa: E402

# Don't start the scheduler during tests.
# In production with Gunicorn, use --preload flag or run scheduler as a separate process
# to avoid multiple scheduler instances across workers.
if not app.config.get("TESTING"):
    start_scheduler()
