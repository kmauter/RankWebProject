import os
from dotenv import load_dotenv

load_dotenv()

# Resolve project root (one level up from this file's directory)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Add it to your .env file or set it in your environment."
        )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Discord bot webhook notification settings
    BOT_NOTIFY_URL = os.getenv("BOT_NOTIFY_URL", "http://localhost:8080/notify")
    BOT_NOTIFY_SECRET = os.getenv("BOT_NOTIFY_SECRET", "")

