# Testing Plan — RankWebProject

This document defines a comprehensive testing strategy to verify all user-facing functionality works correctly. It covers unit tests, integration tests, and manual end-to-end test scripts organized by feature area.

---

## Testing Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Backend Unit/Integration | pytest + pytest-flask | API endpoint testing |
| Backend Fixtures | Factory pattern + in-memory SQLite | Isolated test data |
| Frontend Unit | Jest + React Testing Library | Component rendering & interaction |
| Frontend Integration | Jest + MSW (Mock Service Worker) | API mocking for full flows |
| E2E (future) | Playwright or Cypress | Full browser automation |
| CI | GitHub Actions | Automated on push/PR |

---

## Part 1: Backend Tests

### Test Infrastructure Setup

```
tests/
├── conftest.py          # App factory, test client, DB fixtures
├── test_auth.py         # Registration, login, token handling
├── test_games.py        # Game CRUD, join, settings
├── test_songs.py        # Song submission, deletion, retrieval
├── test_rankings.py     # Ranking CRUD, partial updates
├── test_tasks.py        # Stage transitions, stat calculations
├── test_oauth.py        # Spotify/YouTube OAuth flows
└── test_edge_cases.py   # Error handling, permissions, invalid data
```

**conftest.py fixtures needed:**
- `app` — Flask app with test config (in-memory SQLite, testing=True)
- `client` — Flask test client
- `db` — Fresh database per test
- `auth_token(user)` — Helper to generate valid JWT for a user
- `sample_user` — Pre-created user
- `sample_game` — Pre-created game with owner
- `sample_game_with_players` — Game with 3+ users joined

---

### 1.1 Authentication Tests (`test_auth.py`)

| # | Test Case | Expected Result |
|---|-----------|-----------------|
| 1 | Register with valid data | 201, user created in DB |
| 2 | Register with mismatched passwords | 400, error message |
| 3 | Register with existing username | 400, "User already exists" |
| 4 | Register with existing email | 400, error message |
| 5 | Register with empty username | 400, validation error |
| 6 | Login with valid credentials | 200, returns JWT token |
| 7 | Login with wrong password | 401, "Invalid username or password" |
| 8 | Login with non-existent user | 401, error message |
| 9 | Access protected route with valid token | 200, returns data |
| 10 | Access protected route with expired token | 401, "Token has expired" |
| 11 | Access protected route with no token | 401, error |
| 12 | Access protected route with malformed token | 401, error |
| 13 | Get user profile with valid token | 200, returns username and email |

---

### 1.2 Game Management Tests (`test_games.py`)

| # | Test Case | Expected Result |
|---|-----------|-----------------|
| 1 | Create game with valid data | 201, returns game_code |
| 2 | Create game missing theme | 400, "Missing required fields" |
| 3 | Create game missing dates | 400, "Missing required fields" |
| 4 | Create game with invalid date format | 400, "Invalid date format" |
| 5 | Creator is automatically added as player | GameUser entry exists |
| 6 | Join game with valid code | 200, user added to game |
| 7 | Join game with invalid code | 404, "Game not found" |
| 8 | Join game already joined | 400, "User already part of the game" |
| 9 | Get user games returns all joined games | 200, list includes created and joined games |
| 10 | Get game details as member | 200, returns full game data |
| 11 | Get game details as non-member | 403, "User is not part of the game" |
| 12 | Update submission due date as owner | 200, date updated |
| 13 | Update rank due date as owner | 200, date updated |
| 14 | Update game as non-owner | 403, "Only the game owner can update" |
| 15 | Get players list | 200, returns all players with usernames |
| 16 | Remove player as owner | 200, player removed |
| 17 | Remove player as non-owner | 403, error |
| 18 | Remove non-existent player | 404, error |

---

### 1.3 Song Submission Tests (`test_songs.py`)

| # | Test Case | Expected Result |
|---|-----------|-----------------|
| 1 | Submit song during submission stage | 201, song created |
| 2 | Submit song during ranking stage | 400, "Game is not in the submission stage" |
| 3 | Submit song as non-member | 403, "User is not part of the game" |
| 4 | Submit duplicate song (same title+artist by same user) | 400, "Song already submitted" |
| 5 | Submit song exceeding max limit | 400, "Maximum of X submission(s) reached" |
| 6 | Submit song at exactly max limit - 1 | 201, succeeds |
| 7 | Submit song with missing title | 400, "Missing required fields" |
| 8 | Submit song with missing artist | 400, "Missing required fields" |
| 9 | Submit song with optional comment | 201, comment stored |
| 10 | Get my songs for a game | 200, returns only current user's songs |
| 11 | Get all songs for game (as member) | 200, returns all songs with user info |
| 12 | Get all songs for game (as non-member) | 403, error |
| 13 | Delete song as game owner | 200, song removed |
| 14 | Delete song as non-owner | 403, error |
| 15 | Delete non-existent song | 404, error |

---

### 1.4 Ranking Tests (`test_rankings.py`)

| # | Test Case | Expected Result |
|---|-----------|-----------------|
| 1 | Save full ranking (all songs ranked) | 200, all ranks stored |
| 2 | Save partial ranking (some nulls) | 200, non-null ranks stored |
| 3 | Save ranking replaces previous ranking | Old ranks deleted, new ones stored |
| 4 | Get ranking returns correct order | 200, list matches saved positions |
| 5 | Get ranking when none saved | 200, empty ranking array |
| 6 | Patch ranking updates specific positions | 200, only specified positions changed |
| 7 | Delete ranking removes all user ranks | 200, no ranks remain for user/game |
| 8 | Save ranking with empty list | 400, validation error |
| 9 | Save ranking with invalid song IDs | Gracefully handles (skips nulls) |
| 10 | Multiple users can rank same game independently | Each user's ranking is isolated |

---

### 1.5 Stage Transition Tests (`test_tasks.py`)

| # | Test Case | Expected Result |
|---|-----------|-----------------|
| 1 | Game with past submission_duedate transitions SUBMIT→RANK | Stage updated, song_order set |
| 2 | Song order is randomized | song_order contains all song IDs in shuffled order |
| 3 | Game with no songs transitions without error | Stage updated, no playlist created |
| 4 | Spotify playlist created when owner has token | spotify_playlist_url set |
| 5 | Spotify playlist skipped when owner has no token | spotify_playlist_url remains null |
| 6 | YouTube playlist created when owner has token | youtube_playlist_url set |
| 7 | YouTube playlist skipped when owner has no token | youtube_playlist_url remains null |
| 8 | Game with past rank_duedate transitions RANK→DONE | Stage updated |
| 9 | Stats calculated correctly for simple case | avg_rank, median, range, controversy match expected |
| 10 | User's own songs excluded from their ranking in stats | Self-submitted songs not counted |
| 11 | Game already in DONE stage not re-processed | No duplicate stats |
| 12 | Game with future due dates not transitioned | Stage unchanged |

**Stat calculation verification (test case 9 detail):**
```
Given: 3 users, 6 songs (2 each), rankings submitted
Expected: 
  - avg_rank = mean of all positions for that song
  - median_rank = median of positions
  - rank_range = max_position - min_position
  - controversy = mean absolute deviation from avg
```

---

### 1.6 OAuth Flow Tests (`test_oauth.py`)

| # | Test Case | Expected Result |
|---|-----------|-----------------|
| 1 | Connect Spotify redirects to Spotify auth URL | 302, redirect contains correct params |
| 2 | Spotify callback with valid code stores refresh token | User record updated |
| 3 | Spotify callback with missing code | 400, error |
| 4 | Connect YouTube redirects to Google auth URL | 302, redirect contains correct params |
| 5 | YouTube callback with valid code stores refresh token | User record updated |
| 6 | YouTube callback with missing code | 400, error |

*Note: Actual token exchange should be mocked in tests.*

---

## Part 2: Frontend Tests

### Test Infrastructure

```
client/src/
├── __mocks__/           # Asset mocks (images, fonts)
├── test-utils.js        # Custom render with providers (UserContext, Router)
├── components/
│   ├── LoginForm.test.js
│   ├── RegisterForm.test.js
│   ├── Dashboard.test.js       (expand existing)
│   ├── GameDetails.test.js     (expand existing)
│   ├── GamePreview.test.js
│   ├── CreateRankPopup.test.js (expand existing)
│   ├── JoinRankPopup.test.js
│   ├── GameSettings.test.js
│   └── SettingsPopup.test.js
└── contexts/
    └── UserContext.test.js
```

---

### 2.1 Authentication UI Tests

| # | Component | Test Case | Verify |
|---|-----------|-----------|--------|
| 1 | LoginForm | Renders username and password fields | Fields present and labeled |
| 2 | LoginForm | Submits credentials to /api/login | Axios called with correct payload |
| 3 | LoginForm | Successful login stores token and navigates | localStorage set, navigate('/dashboard') called |
| 4 | LoginForm | Failed login shows error message | "Invalid username or password" displayed |
| 5 | LoginForm | Link to register page exists | Link navigates to /register |
| 6 | RegisterForm | Renders all 4 fields | Username, email, password, confirm password |
| 7 | RegisterForm | Submits to /api/register | Axios called with all fields |
| 8 | RegisterForm | Successful register navigates to login | navigate('/') called |
| 9 | RegisterForm | Link to login page exists | Link navigates to / |
| 10 | UserContext | Loads user from stored token on mount | setUser called with decoded token |
| 11 | UserContext | logout clears token and user | localStorage cleared, user is null |
| 12 | UserContext | Expired token does not set user | user remains null |

---

### 2.2 Dashboard Tests

| # | Test Case | Verify |
|---|-----------|--------|
| 1 | Renders game previews from API | GamePreview components rendered with titles |
| 2 | Shows "Create a rank" and "Join a rank" buttons | Footer buttons present |
| 3 | Clicking game preview opens GameDetails | selectedGame state set, GameDetails rendered |
| 4 | Clicking "Create a rank" shows CreateRankPopup | Popup rendered |
| 5 | Clicking "Join a rank" shows JoinRankPopup | Popup rendered |
| 6 | User menu toggles on icon click | Menu appears/disappears |
| 7 | Logout clears state and redirects | window.location set to '/' |
| 8 | API failure on fetch games redirects to login | window.location set to '/' |

---

### 2.3 Game Creation & Join Tests

| # | Component | Test Case | Verify |
|---|-----------|-----------|--------|
| 1 | CreateRankPopup | Renders form with all fields | Theme, description, dates, limit inputs present |
| 2 | CreateRankPopup | Submit calls onCreate with values | Handler called with correct args |
| 3 | CreateRankPopup | Shows game code after creation | "Game created successfully" + code displayed |
| 4 | CreateRankPopup | Close button calls onClose | Handler called |
| 5 | JoinRankPopup | Renders game code input | Input field present |
| 6 | JoinRankPopup | Submit calls onJoin with code | Handler called with entered code |
| 7 | JoinRankPopup | Close button calls onClose | Handler called |

---

### 2.4 Game Details — Submissions Stage Tests

| # | Test Case | Verify |
|---|-----------|--------|
| 1 | Renders game title and due date | Title and "Due YYYY-MM-DD" shown |
| 2 | Song submission form present | Name, artist, comment fields + submit button |
| 3 | Submitting song calls onSongSubmit | Handler called with name, artist, comment |
| 4 | Form clears after successful submission | All fields reset to empty |
| 5 | User's submitted songs displayed | List shows song names and artists |
| 6 | Delete button on user songs calls onDeleteSong | Handler called with song ID |
| 7 | Owner sees settings button (>>) | Button rendered when currentUser is owner |
| 8 | Non-owner does not see settings button | Button not rendered |
| 9 | Description toggle shows/hides description | Click + shows text, click - hides |
| 10 | Back button calls onBack | Handler called |

---

### 2.5 Game Details — Rankings Stage Tests

| # | Test Case | Verify |
|---|-----------|--------|
| 1 | Song pool displays all songs | All song names rendered in pool |
| 2 | Ranking slots show correct count | Number of slots equals number of songs |
| 3 | Empty slots show "Drop song here" | Placeholder text in unfilled slots |
| 4 | Drag song from pool to slot fills slot | Slot shows song name, pool removes it |
| 5 | Drag song between slots swaps them | Both slots update correctly |
| 6 | Drag song from slot back to pool empties slot | Slot shows placeholder, pool gains song |
| 7 | Save Ranking button calls onSaveRanking | Handler called with current ranking array |
| 8 | Previously saved ranking loads on mount | Slots pre-filled from userRanking prop |
| 9 | Comment expand/collapse works | Click + shows comment, click - hides |
| 10 | Spotify playlist link rendered when available | Link with correct href present |
| 11 | YouTube playlist link rendered when available | Link with correct href present |
| 12 | No playlist links when URLs are null | Links not rendered |

---

### 2.6 Game Details — Results Stage Tests

| # | Test Case | Verify |
|---|-----------|--------|
| 1 | Results table renders with headers | Rank, Song, Artist, Submitted By, Avg, Range, Controversy |
| 2 | Songs displayed in correct order | Sorted by avg_rank ascending (best first) |
| 3 | Statistics display correctly | Avg and controversy show 2 decimal places |
| 4 | Missing stats show dash | '-' displayed when stat is null |
| 5 | Submitted By shows username | User who submitted each song shown |
| 6 | "Finished" label shown instead of "Due" | Date label reflects completed state |

---

### 2.7 Game Settings Tests (Owner Only)

| # | Test Case | Verify |
|---|-----------|--------|
| 1 | Renders submission and rank due date inputs | Date inputs with current values |
| 2 | Changing submission date and saving calls handler | onSaveSubmissionDueDate called with new date |
| 3 | Changing rank date and saving calls handler | onSaveRankDueDate called with new date |
| 4 | All submitted songs listed | Song names and artists shown |
| 5 | Delete song button calls onDeleteSong | Handler called with song ID |
| 6 | All players listed | Usernames shown |
| 7 | Remove button shown for non-owner players | Button present for others, absent for owner |
| 8 | Remove player calls onRemovePlayer | Handler called with game code and player ID |
| 9 | Back button calls onBack | Handler called |
| 10 | Close button calls onGameSettingsClose | Handler called |

---

## Part 3: Manual E2E Test Scripts

These are step-by-step scripts for manual testing before releases. Each script tests a complete user journey.

---

### E2E-1: New User Registration & Login

| Step | Action | Expected |
|------|--------|----------|
| 1 | Navigate to `/` | Login form displayed |
| 2 | Click "Register" link | Navigate to `/register` |
| 3 | Fill in username, email, password, confirm password | All fields accept input |
| 4 | Click "Register" button | Redirected to login page |
| 5 | Enter registered credentials | Fields accept input |
| 6 | Click "Login" | Redirected to `/dashboard`, game grid shown |
| 7 | Refresh page | Still on dashboard (token persisted) |
| 8 | Wait 1+ hours (or manually expire token) | Next API call redirects to login |

---

### E2E-2: Create and Join a Game

| Step | Action | Expected |
|------|--------|----------|
| 1 | Login as User A | Dashboard shown |
| 2 | Click "CREATE A RANK" | Create form appears |
| 3 | Enter theme "Test Songs", dates, limit 3 | Fields filled |
| 4 | Click "Create Game" | Game code displayed (e.g., "ABC123") |
| 5 | Close popup | Game appears in grid with "submissions" icon |
| 6 | Login as User B (different browser/incognito) | Dashboard shown |
| 7 | Click "JOIN A RANK" | Join form appears |
| 8 | Enter game code "ABC123" | Field filled |
| 9 | Click "Join" | Game appears in User B's grid |
| 10 | Try joining same code again | Error (already joined) |
| 11 | Try joining invalid code "ZZZZZ" | Error (game not found) |

---

### E2E-3: Song Submission Flow

| Step | Action | Expected |
|------|--------|----------|
| 1 | Click game in submissions stage | GameDetails opens with form |
| 2 | Submit "Imagine" by "John Lennon" with comment | Song appears in "Your Submitted Songs" |
| 3 | Submit "Hey Jude" by "The Beatles" | Second song appears |
| 4 | Submit "Let It Be" by "The Beatles" | Third song appears |
| 5 | Try submitting a 4th song (if limit is 3) | Error message about max submissions |
| 6 | Delete "Hey Jude" | Song removed from list |
| 7 | Submit "Yesterday" by "The Beatles" | Succeeds (back under limit) |
| 8 | As owner, click ">>" to open settings | Settings page shows all songs from all users |

---

### E2E-4: Stage Transition (SUBMIT → RANK)

| Step | Action | Expected |
|------|--------|----------|
| 1 | Set submission due date to past date (via settings) | Date saved |
| 2 | Wait for scheduler (or run `python app/test_tasks.py`) | Game transitions |
| 3 | Refresh dashboard | Game icon changes to "rankings" |
| 4 | Click game | Rankings UI shown with song pool |
| 5 | Verify songs are in randomized order | Order differs from submission order |
| 6 | If owner connected Spotify: verify playlist link | Link opens valid Spotify playlist |
| 7 | If owner connected YouTube: verify playlist link | Link opens valid YouTube playlist |

---

### E2E-5: Ranking Flow

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open game in rankings stage | Song pool and empty ranking slots shown |
| 2 | Drag first song to slot 1 | Song appears in slot, removed from pool |
| 3 | Drag second song to slot 2 | Slot filled |
| 4 | Drag song from slot 1 to slot 3 | Songs swap positions |
| 5 | Drag song from slot back to pool | Slot empties, song returns to pool |
| 6 | Fill all slots | Pool shows "No songs left" |
| 7 | Click "Save Ranking" | Ranking saved (no error) |
| 8 | Navigate away and return to game | Ranking loads in saved order |
| 9 | Change ranking and save again | New order persists |
| 10 | Test on mobile (touch drag) | Drag works with touch sensors |

---

### E2E-6: Stage Transition (RANK → DONE) & Results

| Step | Action | Expected |
|------|--------|----------|
| 1 | Ensure multiple users have submitted rankings | At least 2 users ranked |
| 2 | Set rank due date to past (or run test_tasks.py) | Game transitions to DONE |
| 3 | Refresh dashboard | Game icon changes to "results" |
| 4 | Click game | Results table displayed |
| 5 | Verify songs sorted by average rank | Best (lowest avg) at top |
| 6 | Verify "Submitted By" column | Correct usernames shown |
| 7 | Verify statistics make sense | Avg, range, controversy are reasonable numbers |
| 8 | Check that user's own songs were excluded from their ranking | Stats reflect only other users' rankings |

---

### E2E-7: Owner Management

| Step | Action | Expected |
|------|--------|----------|
| 1 | As owner, open game settings | Settings page loads |
| 2 | Change submission due date | Date updates on save |
| 3 | Change rank due date | Date updates on save |
| 4 | View all submitted songs | All songs from all users listed |
| 5 | Delete a song | Song removed from list |
| 6 | View all players | All players listed |
| 7 | Remove a player (not self) | Player removed |
| 8 | Verify removed player no longer sees game | Game gone from their dashboard |
| 9 | Verify owner cannot remove themselves | No remove button next to owner |

---

### E2E-8: Spotify & YouTube Connection

| Step | Action | Expected |
|------|--------|----------|
| 1 | Click user icon → Settings | Settings popup appears |
| 2 | Click "Connect Spotify" | New tab opens Spotify auth page |
| 3 | Authorize the app | Tab shows "Spotify account connected!" |
| 4 | Close tab, create a game, submit songs, trigger transition | Spotify playlist URL set on game |
| 5 | Click Spotify playlist link | Opens valid playlist with correct songs |
| 6 | Repeat steps 2-5 for YouTube | YouTube playlist created and accessible |

---

### E2E-9: Error Handling & Edge Cases

| Step | Action | Expected |
|------|--------|----------|
| 1 | Access /dashboard without logging in | Redirected to login (after auth guard is added) |
| 2 | Let token expire, try any action | Graceful redirect to login with message |
| 3 | Submit song with very long name (200+ chars) | Handled gracefully (truncated or rejected) |
| 4 | Create game with submission date after rank date | Should warn or prevent |
| 5 | Join game that's already in ranking stage | Should still allow joining |
| 6 | Rank a game with only 1 song | UI handles single-item ranking |
| 7 | Game with 0 songs transitions | No crash, no playlist created |
| 8 | Two users submit same song (same title/artist) | Both allowed (different users) |
| 9 | Rapidly click "Save Ranking" multiple times | No duplicate saves or errors |
| 10 | Open same game in two tabs, submit in both | Second tab reflects first tab's submission |

---

## Part 4: Test Coverage Goals

| Area | Target Coverage | Priority |
|------|----------------|----------|
| Auth endpoints | 90%+ | High |
| Game CRUD endpoints | 85%+ | High |
| Song submission logic | 85%+ | High |
| Ranking CRUD | 80%+ | High |
| Stage transition logic | 90%+ | High (most complex logic) |
| OAuth flows | 60%+ (mocked) | Medium |
| Frontend auth components | 80%+ | Medium |
| Frontend Dashboard | 70%+ | Medium |
| Frontend GameDetails | 75%+ | High |
| Frontend GameSettings | 70%+ | Medium |

---

## Part 5: CI Integration

### Target Pipeline

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup Python 3.10
      - pip install -r requirements.txt
      - pip install pytest pytest-flask
      - pytest tests/ --cov=app --cov-report=term

  frontend:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup Node 20
      - npm ci (client/)
      - npm run build (client/)    # Verify build succeeds
      - npx react-scripts test --watchAll=false --coverage (client/)

  lint:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - ruff check app/            # Python linting
      - cd client && npx eslint src/  # JS linting
```

### Pass/Fail Criteria
- All tests must pass
- Build must succeed
- No lint errors (warnings acceptable initially)
- Coverage must not decrease on PRs (enforce via coverage comments)
