# RankWebProject — Backend Documentation

## Overview

The backend is a **Python Flask** REST API that powers a collaborative music ranking game. Users create themed games, invite friends via codes, submit songs, rank them via drag-and-drop, and view computed statistics. The backend handles authentication, game lifecycle, song management, ranking logic, and integrations with Spotify and YouTube for automatic playlist creation.

**Production URL:** `https://rankwebgame.com/api`

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask |
| ORM | Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Database | SQLite (dev), PostgreSQL-ready (psycopg2-binary in deps) |
| Auth | PyJWT (HS256), Werkzeug password hashing |
| Background Jobs | APScheduler (BackgroundScheduler) |
| Spotify | Spotipy + raw requests for token refresh |
| YouTube | Google API Python Client + raw requests |
| Env Config | python-dotenv |

---

## Project Structure

```
app/
├── __init__.py          # Flask app factory, DB init, scheduler start
├── config.py            # Config class (SECRET_KEY, DB URI from env)
├── models.py            # SQLAlchemy models (User, Game, GameUser, Song, Rank, SongStat)
├── routes.py            # All API endpoints
├── tasks.py             # APScheduler job: game stage transitions
├── spotifyactions.py    # Spotify playlist creation logic
├── youtubeactions.py    # YouTube playlist creation logic
├── test_playlistactions.py  # Manual test script for playlist creation
├── test_tasks.py        # Manual test script for stage transitions
├── .env                 # Environment variables (secrets, API keys)
run.py                   # Entry point: `python run.py`
requirements.txt         # Python dependencies (unpinned)
app.db                   # SQLite database file
migrations/              # Alembic migration files
```

---

## Database Schema

### User
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| username | String | Unique, not null |
| email | String | Unique, not null |
| password_hash | String | Werkzeug hashed |
| spotify_refresh_token | String | Nullable, OAuth |
| youtube_refresh_token | String | Nullable, OAuth |

### Game
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| owner_id | FK → User.id | Game creator |
| theme | String | Game title/theme |
| description | String | Nullable |
| stage | Enum(Stage) | SUBMIT / RANK / DONE |
| submission_duedate | Date | |
| rank_duedate | Date | |
| game_code | String | Unique 6-char alphanumeric |
| max_submissions_per_user | Integer | Default 2 |
| spotify_playlist_url | String | Nullable, set on stage transition |
| youtube_playlist_url | String | Nullable, set on stage transition |
| song_order | JSON | Randomized song IDs for ranking |

### GameUser (Join Table)
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| game_id | FK → Game.id | |
| user_id | FK → User.id | |
| | | Unique constraint on (game_id, user_id) |

### Song
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| user_id | FK → User.id | Submitter |
| game_id | FK → Game.id | |
| title | String | |
| artist | String | |
| comment | String | Nullable |

### Rank
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| game_id | FK → Game.id | |
| user_id | FK → User.id | |
| song_id | FK → Song.id | |
| rank_position | Integer | 1-indexed position |
| | | Unique on (game_id, user_id, song_id) |
| | | Unique on (game_id, user_id, rank_position) |

### SongStat
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| song_id | FK → Song.id | |
| game_id | FK → Game.id | |
| avg_rank | Float | |
| median_rank | Float | |
| rank_range | Integer | max - min |
| controversy | Float | Mean absolute deviation |

---

## API Endpoints

### Authentication
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/register` | Create account (username, email, password, password2) |
| POST | `/api/login` | Returns JWT token (1hr expiry) |
| GET | `/api/user-profile` | Get current user info |

### Games
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/games` | Create game (theme, description, dates, max submissions) |
| POST | `/api/join-game` | Join game by code |
| GET | `/api/user-games` | List all games for current user |
| GET | `/api/game/<code>` | Get single game details |
| PATCH | `/api/game/<code>/update-game` | Update due dates (owner only) |

### Songs
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/submit-song` | Submit song to game |
| GET | `/api/my-game-songs?game_code=X` | Get user's songs for a game |
| GET | `/api/game/<code>/songs` | All songs in game (with stats if available) |
| DELETE | `/api/song/<id>` | Delete song (owner only) |

### Players
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/game/<code>/players` | List players in game |
| DELETE | `/api/game/<code>/player/<id>` | Remove player (owner only) |

### Rankings
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/game/<code>/rankings` | Get current user's ranking |
| POST | `/api/game/<code>/rankings` | Save full ranking (list of song IDs) |
| PATCH | `/api/game/<code>/rankings` | Partial update (list of {song_id, rank_position}) |
| DELETE | `/api/game/<code>/rankings` | Delete all user rankings for game |

### OAuth / External Services
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/connect-spotify?user_id=X` | Start Spotify OAuth flow |
| GET | `/api/spotifycallback` | Spotify OAuth callback |
| GET | `/api/connect-youtube?user_id=X` | Start YouTube OAuth flow |
| GET | `/api/youtubecallback` | YouTube OAuth callback |

---

## Background Scheduler (tasks.py)

Runs every **1 hour** via APScheduler. Performs two transitions:

### SUBMIT → RANK (when `submission_duedate` passes)
1. Fetches all songs for the game
2. Randomizes song order, stores in `game.song_order`
3. Creates Spotify playlist (if owner has connected Spotify)
4. Creates YouTube playlist (if owner has connected YouTube)
5. Sets `game.stage = Stage.RANK`

### RANK → DONE (when `rank_duedate` passes)
1. Gathers all rankings for the game
2. For each user, filters out songs they submitted from their ranking
3. Calculates per-song statistics: avg rank, median, range, controversy (MAD)
4. Stores stats in `SongStat` table
5. Sets `game.stage = Stage.DONE`

---

## Environment Variables (.env)

```
SECRET_KEY=<jwt-signing-key>
DATABASE_URL=<sqlalchemy-connection-string>
SPOTIFY_CLIENT_ID=<spotify-app-client-id>
SPOTIFY_CLIENT_SECRET=<spotify-app-client-secret>
SPOTIFY_REDIRECT_URI=<e.g. http://127.0.0.1:5000/api/spotifycallback>
YOUTUBE_CLIENT_ID=<google-oauth-client-id>
YOUTUBE_CLIENT_SECRET=<google-oauth-client-secret>
YOUTUBE_REDIRECT_URI=<e.g. http://127.0.0.1:5000/api/youtubecallback>
```

---

## Known Pain Points & Critical Issues

### Critical
1. **Duplicate import in `__init__.py`** — `from app import routes, models` is imported twice, causing routes to register twice (potential duplicate responses or errors).
2. **Hardcoded secret key fallback** — `config.py` defaults to `"k5Gm3o9e902DM0G4"` if `SECRET_KEY` env var is missing. This is a security risk in production.
3. **Hardcoded absolute DB path** — `config.py` falls back to `sqlite:///C:/Users/kylem/...` which breaks on any other machine.
4. **No token refresh on frontend** — JWT expires in 1 hour with no refresh mechanism. Users get silently logged out.
5. **`config.py` in .gitignore but committed** — The app/config.py is gitignored but already tracked, creating confusion about secret management.

### Security
6. **OAuth `user_id` passed as query param** — `/api/connect-spotify?user_id=X` allows any user to connect Spotify to any account. Should use the JWT token instead.
7. **No rate limiting** — Login, registration, and song submission have no rate limits.
8. **No input sanitization** — Beyond basic null checks, no XSS or injection protection.
9. **Plain-text error responses** — Some endpoints return plain strings (e.g., `'User already exists'`) without proper HTTP status codes.

### Performance
10. **N+1 queries** — `get_user_games` and `get_game_songs_details` call `User.query.get()` inside loops.
11. **No database indexing** beyond primary keys and unique constraints.
12. **Scheduler runs in every Gunicorn worker** — In production with multiple workers, the scheduler fires multiple times per interval.

### Code Quality
13. **No backend tests in CI** — Only frontend tests run in GitHub Actions.
14. **Unpinned dependencies** — `requirements.txt` has no version pins, risking breaking changes.
15. **Inconsistent date handling** — Uses `datetime.utcnow()` (deprecated in Python 3.12+) mixed with `datetime.now(timezone.utc)`.
16. **No proper error handling decorator** — Each route has its own try/except with duplicated JWT error handling.
17. **`delete_song` only allows owner** — Users cannot delete their own submissions, only the game owner can.

---

## How to Run Locally

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# From project root
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file in app/ directory with required variables (see above)

# Initialize database (first time)
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### Run
```bash
python run.py
```
Server starts at `http://127.0.0.1:5000`

### Run Backend Tests (manual)
```bash
python app/test_tasks.py        # Tests stage transition logic
python app/test_playlistactions.py  # Tests Spotify/YouTube playlist creation
```

---

## How to Deploy to Production

The project is deployed on a **DigitalOcean Droplet** with:
- **Gunicorn** as the WSGI server
- **Nginx** as reverse proxy
- **Let's Encrypt** for HTTPS
- Domain: `rankwebgame.com`

### Deployment Steps
1. SSH into the server
2. Pull latest code: `git pull origin main`
3. Activate venv: `source .venv/bin/activate`
4. Install deps: `pip install -r requirements.txt`
5. Run migrations: `flask db upgrade`
6. Build frontend: `cd client && npm run build`
7. Restart Gunicorn: `sudo systemctl restart gunicorn`
8. Nginx serves the React build from `client/build/`

### Production Considerations
- Run scheduler as a **separate process** (not inside Gunicorn workers)
- Set `SPOTIFY_REDIRECT_URI` and `YOUTUBE_REDIRECT_URI` to production URLs
- Add production redirect URIs to Spotify Dashboard and Google Cloud Console
- Publish Google OAuth consent screen (move from testing to production)
- Ensure `SECRET_KEY` is a strong random value, not the fallback

---

## How to Test in Production

1. Register a new account at `https://rankwebgame.com`
2. Create a game with a theme and due dates
3. Share the game code with other users
4. Submit songs during the submission phase
5. Wait for (or manually trigger) the stage transition
6. Verify Spotify/YouTube playlists are created
7. Rank songs during the ranking phase
8. Verify results and statistics after rank due date passes

### Manual Stage Transition (for testing)
```bash
# SSH into server, activate venv
python app/test_tasks.py
```
This immediately runs the stage transition logic regardless of due dates.
