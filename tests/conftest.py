"""
Test configuration and shared fixtures for RankWebProject backend tests.

Uses an in-memory SQLite database so tests are fast and isolated.
"""
import pytest
import jwt
from datetime import datetime, timedelta, date

# Override config BEFORE importing the app so the global instance picks it up
import os
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app as flask_app, db
from app.models import User, Game, GameUser, Song, Rank, Stage

# Disable rate limiter for tests
from app import limiter
limiter.enabled = False


@pytest.fixture(autouse=True)
def app():
    """Configure the Flask app for testing and provide a fresh DB per test."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "RATELIMIT_ENABLED": False,
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create and return a sample user."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(app):
    """Create and return a second user for multi-user tests."""
    user = User(username="seconduser", email="second@example.com")
    user.set_password("password456")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_game(app, sample_user):
    """Create a game owned by sample_user with the user already joined."""
    game = Game(
        owner_id=sample_user.id,
        theme="Test Theme",
        description="A test game",
        stage=Stage.SUBMIT,
        submission_duedate=date(2026, 6, 1),
        rank_duedate=date(2026, 6, 15),
        game_code="TEST01",
        max_submissions_per_user=3,
    )
    db.session.add(game)
    db.session.commit()

    # Owner is automatically a player
    game_user = GameUser(game_id=game.id, user_id=sample_user.id)
    db.session.add(game_user)
    db.session.commit()

    return game


@pytest.fixture
def sample_game_with_players(app, sample_game, second_user):
    """A game with the owner + a second player joined."""
    game_user = GameUser(game_id=sample_game.id, user_id=second_user.id)
    db.session.add(game_user)
    db.session.commit()
    return sample_game


def make_auth_header(user_id, secret="test-secret-key", expired=False):
    """Helper to generate a JWT Authorization header for a given user."""
    exp = datetime.utcnow() + timedelta(hours=1)
    if expired:
        exp = datetime.utcnow() - timedelta(hours=1)

    token = jwt.encode(
        {"user_id": user_id, "exp": exp},
        secret,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}
