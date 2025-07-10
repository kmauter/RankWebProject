from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]  # Set secret key immediately after config
# print("SECRET_KEY at startup:", app.secret_key)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models  # Import routes and models after db and migrate are initialized
from app.tasks import start_scheduler  # Import tasks after db and migrate are initialized
start_scheduler()

from app import routes, models  # Import routes after secret key is set