import os
from dotenv import load_dotenv

# Load the shared .env file from app/ directory
_env_path = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "app",
    ".env",
)
load_dotenv(_env_path)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
BOT_NOTIFY_SECRET = os.getenv("BOT_NOTIFY_SECRET", "")
FLASK_API_URL = os.getenv("FLASK_API_URL", "http://127.0.0.1:5000")
BOT_HTTP_PORT = int(os.getenv("BOT_HTTP_PORT", "8080"))
