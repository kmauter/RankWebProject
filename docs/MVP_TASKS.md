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

- [ ] **Add auth guard on `/dashboard` route** — Redirect to login if no valid token exists. Check token expiry on mount.
- [ ] **Handle 401 responses globally on frontend** — When any API call returns 401, clear token and redirect to login with a message.
- [ ] **Extend JWT expiry or add refresh tokens** — 1 hour is too short for a game session. Either extend to 24h+ or implement a `/api/refresh-token` endpoint.
- [ ] **Decode and validate token expiry in `UserContext`** — On app load, check if stored token is expired before setting user state.

---

## P3 — Data Integrity & Backend Robustness

- [ ] **Add a shared auth decorator** — Replace duplicated try/except JWT handling in every route with a `@require_auth` decorator.
- [ ] **Fix N+1 queries** — In `get_user_games` and `get_game_songs_details`, use `joinedload` or batch queries instead of `User.query.get()` in loops.
- [ ] **Allow users to delete their own song submissions** — Currently only the game owner can delete songs. Users should be able to delete their own during submission stage.
- [ ] **Add database indexes** — Add indexes on `GameUser.user_id`, `Song.game_id`, `Rank.game_id`, `Rank.user_id` for query performance.
- [ ] **Pin dependency versions in `requirements.txt`** — Run `pip freeze > requirements.txt` to lock versions.
- [ ] **Replace deprecated `datetime.utcnow()`** — Use `datetime.now(timezone.utc)` consistently (already used in tasks.py, not in routes.py).

---

## P4 — Frontend UX (Minimum viable experience)

- [ ] **Add loading states** — Show a spinner or skeleton while fetching games, songs, and rankings.
- [ ] **Show error messages to users** — Display toast/banner when API calls fail (song submission, join game, create game, save ranking).
- [ ] **Add confirmation dialogs** — Confirm before: deleting a song, removing a player, logging out.
- [ ] **Show registration errors from backend** — Display "User already exists" or "Passwords do not match" messages in the RegisterForm.
- [ ] **Remove console.log statements** — Strip all debug logging from production code.
- [ ] **Remove dead code** — Delete `GamePopup.js`, remove commented-out blocks in Dashboard.js.
- [ ] **Remove unused `react-beautiful-dnd` dependency** — Only `@dnd-kit` is used.

---

## P5 — Testing (Minimum coverage for confidence)

### Backend Tests
- [ ] **Set up pytest with test fixtures** — Create `tests/` directory, configure test database (in-memory SQLite), add app factory pattern or test client.
- [ ] **Test auth endpoints** — Register, login, invalid credentials, duplicate user, token generation.
- [ ] **Test game CRUD** — Create game, join game, duplicate join, invalid code, owner-only operations.
- [ ] **Test song submission** — Submit, max limit enforcement, duplicate detection, delete permissions.
- [ ] **Test ranking CRUD** — Save ranking, partial update, delete, retrieve.
- [ ] **Test stage transitions** — Mock dates, verify SUBMIT→RANK and RANK→DONE logic, stat calculations.

### Frontend Tests
- [ ] **Test LoginForm** — Successful login sets token, failed login shows error.
- [ ] **Test RegisterForm** — Successful register navigates to login, validation errors display.
- [ ] **Test GameDetails submissions** — Song form submits, user songs display, delete works.
- [ ] **Test GameDetails rankings** — Drag-and-drop state updates, save calls API.
- [ ] **Test auth guard behavior** — Unauthenticated user redirected to login.

### CI Pipeline
- [ ] **Add backend test job to GitHub Actions** — Install Python deps, run pytest.
- [ ] **Add `npm run build` step** — Verify production build succeeds on every push.
- [ ] **Add linting step** — ESLint for frontend, flake8 or ruff for backend.

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
