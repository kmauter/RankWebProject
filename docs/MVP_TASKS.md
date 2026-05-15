# MVP Task List — Production Ready & Tested

This is a prioritized task list to get RankWebProject stable, secure, and tested for production use. Tasks are grouped by category and ordered by impact. Each task is scoped to be individually completable.

---

## P0 — Critical Bugs (Fix Immediately)

- [x] **Remove duplicate import in `app/__init__.py`** — `from app import routes, models` appeared twice, causing routes to double-register. Removed the second import on line 18.
- [x] **Fix results table sort order** — `GameDetails.js` sorted by nonexistent `finalRank` (always undefined, making sort a no-op) then called `.reverse()`. Fixed to sort by `avg_rank` ascending (lowest avg = best rank = #1) and removed `.reverse()`. Rank column now displays position in sorted array (`idx + 1`) instead of the missing `finalRank` property.
- [x] **Fix hardcoded absolute DB path in `app/config.py`** — Replaced the absolute path (`sqlite:///C:/Users/kylem/...`) with a relative path computed from `BASE_DIR` (project root). Now resolves to `<project_root>/app.db` on any machine. Still respects `DATABASE_URL` env var if set.

---

## P1 — Security (Must-fix before public launch)

- [x] **Remove hardcoded secret key fallback** — `config.py` now raises `RuntimeError` on startup if `SECRET_KEY` env var is not set. No more insecure default.
- [x] **Fix OAuth endpoints to use JWT instead of query param `user_id`** — `/api/connect-spotify` and `/api/connect-youtube` now extract user_id from the JWT Authorization header. Returns 401 if no valid token is provided.
- [x] **Return proper HTTP status codes on all error responses** — `/api/register` now returns JSON responses with 201 on success, 400 on validation errors (missing fields, mismatched passwords, duplicate user/email).
- [x] **Add rate limiting to auth endpoints** — Added `flask-limiter`: `/api/register` limited to 5/min, `/api/login` limited to 10/min.
- [x] **Validate and sanitize all user inputs** — Register: username 3-30 chars (alphanumeric + hyphens/underscores), email format check, password min 6 chars. Song submission: title/artist max 200 chars, comment max 500 chars, inputs stripped.
- [x] **Ensure scheduler runs only once in production** — Scheduler no longer starts when `TESTING=True`. Added comment documenting Gunicorn `--preload` flag requirement for production. Also fixed a likely production bug: `update_game_stages()` was comparing `Date` columns against a timezone-aware `datetime` object — changed to compare against `.date()` so the query filter works correctly across all database backends.

---

## P2 — Auth & Session Stability

- [x] **Add auth guard on `/dashboard` route** — Created `ProtectedRoute` component that checks for valid user/token in context. Wraps the Dashboard route in App.js — redirects to login if not authenticated.
- [x] **Handle 401 responses globally on frontend** — Created `installGlobal401Handler()` in `utils/api.js` that monkey-patches `window.fetch` to intercept 401 responses from `/api/*` endpoints, clear the token, and redirect to login. Installed in `index.js` at app startup.
- [x] **Extend JWT expiry or add refresh tokens** — Extended JWT expiry from 1 hour to 24 hours. Sufficient for game sessions without the complexity of refresh tokens.
- [x] **Decode and validate token expiry in `UserContext`** — On app load, `UserContext` now checks `exp` claim against current time. If expired, clears token from localStorage and does not set user state.

---

## P3 — Data Integrity & Backend Robustness

- [x] **Add a shared auth decorator** — Created `@require_auth` decorator in `routes.py` that extracts `user_id` from JWT into `g.user_id`, returns 401 JSON for missing/expired/invalid tokens. Available for gradual migration of existing routes.
- [x] **Fix N+1 queries** — Replaced `User.query.get()` inside loops with batch queries in `get_user_games`, `get_game_songs_details`, and `get_game_players`. Users and stats are now fetched in single queries and looked up from dictionaries.
- [x] **Allow users to delete their own song submissions** — Updated delete song endpoint to allow deletion if user is the game owner OR the song's original submitter. Non-owners can only delete their own songs.
- [x] **Add database indexes** — Added `index=True` on `GameUser.user_id`, `GameUser.game_id`, `Song.user_id`, `Song.game_id`, `Rank.game_id`, `Rank.user_id` for query performance. Requires `flask db migrate` + `flask db upgrade` on deploy.
- [x] **Pin dependency versions in `requirements.txt`** — All dependencies now pinned to exact versions (e.g., `Flask==3.1.0`, `SQLAlchemy==2.0.40`).
- [x] **Replace deprecated `datetime.utcnow()`** — Login route now uses `datetime.now(timezone.utc)` consistently with tasks.py.

---

## Discovered Issues (found during P4 work)

- [x] **`except Exception` returns 401 for non-auth errors** — Fixed all 16 route handlers: JWT/auth errors (ExpiredSignature, InvalidToken, missing header) return 401, all other exceptions return 500. Prevents non-auth errors from triggering the global logout redirect.
- [x] **`max_submissions_per_user` stored as string in some DB rows** — Frontend was sending empty string or string numbers. Fixed: `int(data.get('maxSubmissionsPerUser') or 2)` in create-game ensures integer storage. Added `int()` cast on comparison for old data safety.
- [x] **OAuth connect endpoints used `window.open` with query param** — Frontend couldn't send JWT via `window.open()`. Changed backend to return auth URL as JSON (200) instead of 302 redirect. Frontend now fetches with JWT header, then opens the returned URL.
- [x] **Spotify callback logged client secret** — Removed `print()` that exposed `SPOTIFY_CLIENT_SECRET` in logs.
- [x] **YouTube callback didn't check if user exists** — Added null check before setting `youtube_refresh_token`, preventing `AttributeError` crash.

### Remaining config note
- Production `.env` must have correct redirect URIs for Spotify/YouTube callbacks (e.g., `https://rankwebgame.com/api/spotifycallback`). These must also be registered in the Spotify Dashboard and Google Cloud Console.

---

## P4 — Frontend UX (Minimum viable experience)

- [ ] **Add loading states** *(deferred — requests are fast enough, revisit if performance degrades)*
- [x] **Show error messages to users** — Added notification banner system to Dashboard. Red banner for errors (song submission, join game, create game, save ranking failures), green banner for success (ranking saved). Auto-dismisses after 4 seconds. Uses HandFont and existing color variables.
- [x] **Add confirmation dialogs** — Created `ConfirmDialog` component with overlay. Wired to delete song, remove player, and logout actions. Uses HandFont, existing color variables, centered modal with Cancel/Confirm buttons.
- [x] **Show registration errors from backend** — RegisterForm now displays backend error messages ("User already exists", "Passwords do not match", etc.) using the existing `.error-message` style.
- [x] **Remove console.log statements** — Removed 45 console.log/error/warn statements from all source files.
- [x] **Remove dead code** — Deleted unused `GamePopup.js`.
- [x] **Remove unused `react-beautiful-dnd` dependency** — Uninstalled from package.json.

---

## P5 — Testing (Minimum coverage for confidence)

### Backend Tests
- [x] **Set up pytest with test fixtures** — `tests/conftest.py` with in-memory SQLite, test client, reusable fixtures (`sample_user`, `sample_game`, etc.), and `make_auth_header()` helper.
- [x] **Test auth endpoints** — 12 tests covering register, login, invalid credentials, duplicate user, token validation, expiry.
- [x] **Test game CRUD** — 14 tests covering create, join, duplicate join, invalid code, owner-only operations, players.
- [x] **Test song submission** — 15 tests covering submit, max limit, duplicate detection, delete permissions (owner + self).
- [x] **Test ranking CRUD** — 8 tests covering save, partial update, delete, retrieve, multi-user isolation.
- [x] **Test stage transitions** — 15 tests covering SUBMIT→RANK, RANK→DONE, playlist creation, stat calculations, date filtering.

### Frontend Tests
- [x] **Test LoginForm** — 5 tests: renders fields, successful login stores token + navigates, failed login shows error, register link present.
- [x] **Test RegisterForm** — 4 tests: renders all fields, successful register navigates to login, login link present.
- [x] **Test auth guard behavior** — 3 tests: redirects without user, redirects without token, renders with both.
- [x] **Test UserContext** — 4 tests: loads from valid token, rejects expired token, logout clears state, no token = no user.

### CI Pipeline
- [x] **Add backend test job to GitHub Actions** — Python 3.10, installs deps, runs pytest with in-memory SQLite.
- [x] **Add `npm run build` step** — Verifies production build succeeds on every push.
- [x] **Add linting step** — ruff for backend (E/F/W rules), ESLint for frontend (max 50 warnings).

---

## P6 — Deployment Hardening

- [ ] **Document all required env vars** — Create `.env.example` with placeholder values for both dev and production.
- [ ] **Add health check endpoint** — `GET /api/health` returns 200 with DB connectivity status.
- [ ] **Configure CORS properly** — Add `flask-cors` with explicit allowed origins for production domain.
- [ ] **Add request logging** — Use Python `logging` module instead of `print()` statements throughout backend.
- [ ] **Set up error monitoring** — Add Sentry or similar for uncaught exceptions in production.
- [ ] **Automate deployment** — Add a GitHub Actions deploy job (SSH + pull + build + restart) triggered on main branch push.

---

## Out of Scope (Post-MVP)

These are noted in the README roadmap but not required for production readiness:
- Docker containerization
- User profile pictures
- Detailed user statistics
- Game deletion by owner
- Email verification
- Spotify audio features (loudness, happiness)
- Spreadsheet export
- Winner display
- Update login/register page styling to match the dashboard aesthetic
- Restyle confirmation dialog to match the paper/hand-drawn theme

---

## Suggested Order of Execution

1. **P0** — Fix the three critical bugs (30 min)
2. **P1** — Security fixes (2-3 hours)
3. **P2** — Auth stability (1-2 hours)
4. **P3** — Backend robustness (2-3 hours)
5. **P5 Backend Tests** — Write tests while fixing P3 (3-4 hours)
6. **P4** — Frontend UX (2-3 hours)
7. **P5 Frontend Tests + CI** — (2-3 hours)
8. **P6** — Deployment hardening (2-3 hours)

**Estimated total: 15-20 hours of focused work.**
