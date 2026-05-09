# RankWebProject — Frontend Documentation

## Overview

The frontend is a **React 18** single-page application (Create React App) that provides the UI for a collaborative music ranking game. Users register/login, create or join games, submit songs, drag-and-drop rank them, and view results with statistics. The app has a distinctive hand-drawn/notebook aesthetic using custom fonts and decorative corner images.

**Production URL:** `https://rankwebgame.com`

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 18 (Create React App) |
| Routing | React Router DOM v6 |
| State | React Context (UserContext) + local component state |
| HTTP | Axios (auth forms), Fetch API (dashboard/game actions) |
| Drag & Drop | @dnd-kit/core + @dnd-kit/sortable |
| Styling | Custom CSS + Tailwind CSS + Bootstrap |
| Auth | JWT (jwt-decode), stored in localStorage |
| Testing | Jest + React Testing Library |

---

## Project Structure

```
client/
├── public/
│   ├── index.html           # HTML shell
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── App.js               # Router setup, top-level routes
│   ├── App.test.js          # Smoke test
│   ├── index.js             # ReactDOM entry, wraps in UserProvider
│   ├── reportWebVitals.js
│   ├── components/
│   │   ├── Routes.js        # Route path constants
│   │   ├── LoginForm.js     # Login page (axios)
│   │   ├── RegisterForm.js  # Registration page (axios)
│   │   ├── HomePage.js      # Landing page (minimal)
│   │   ├── Dashboard.js     # Main game hub (fetches, state management)
│   │   ├── Header.js        # Top bar with logo + user icon
│   │   ├── Footer.js        # Bottom bar with Join/Create buttons
│   │   ├── GamePreview.js   # Game card in dashboard grid
│   │   ├── GameDetails.js   # Full game view (submissions/rankings/results)
│   │   ├── GameSettings.js  # Owner settings (dates, songs, players)
│   │   ├── GamePopup.js     # [DEAD CODE] Legacy popup, replaced by GameDetails
│   │   ├── CreateRankPopup.js  # Create game form
│   │   ├── JoinRankPopup.js    # Join game form
│   │   ├── SettingsPopup.js    # Spotify/YouTube connect buttons
│   │   ├── FormContainer.js    # Reusable form wrapper
│   │   ├── FormField.js        # Reusable form input
│   │   ├── Draggable.js        # dnd-kit draggable wrapper
│   │   ├── Droppable.js        # dnd-kit droppable wrapper
│   │   ├── Dashboard.test.js
│   │   ├── CreateRankPopup.test.js
│   │   └── GameDetails.test.js
│   ├── contexts/
│   │   └── UserContext.js   # Auth state (user, setUser, logout)
│   ├── styles/
│   │   ├── index.css        # Main stylesheet (all app styles)
│   │   ├── App.css          # Minimal/unused
│   │   ├── CustomButton.css # Tailwind @apply button
│   │   └── GamePreview.css  # Game card styles
│   ├── assets/              # Images (corners, logos, backgrounds, icons)
│   └── fonts/               # HandFont custom font files
├── package.json
├── postcss.config.js        # PostCSS with Tailwind + Autoprefixer
└── build/                   # Production build output
```

---

## Routing

| Path | Component | Description |
|------|-----------|-------------|
| `/` | LoginForm | Default landing, login form |
| `/home` | HomePage | Simple links to login/register |
| `/register` | RegisterForm | Account creation |
| `/dashboard` | Dashboard | Main app (requires auth) |

Route constants defined in `components/Routes.js`:
```js
export const routes = {
    home: '/home',
    login: '/',
    register: '/register',
};
```

---

## Component Architecture

### App Flow
```
index.js
  └── UserProvider (context)
       └── App.js (Router)
            ├── LoginForm
            ├── RegisterForm
            ├── HomePage
            └── Dashboard
                 ├── Header
                 ├── GamePreview[] (grid)
                 ├── GameDetails (submissions | rankings | results)
                 │    ├── Draggable / Droppable (rankings mode)
                 │    └── Results table (results mode)
                 ├── CreateRankPopup
                 ├── JoinRankPopup
                 ├── GameSettings (owner only)
                 ├── SettingsPopup (Spotify/YouTube connect)
                 └── Footer
```

### State Management
- **UserContext** — Global auth state. Reads JWT from localStorage on mount, provides `user`, `setUser`, `logout`.
- **Dashboard** — Central state hub. Manages: selected game, popups visibility, game previews, songs, players, rankings, due dates. All API calls originate here and pass data/handlers down as props.
- **GameDetails** — Local state for form inputs, drag-and-drop ranking arrays, comment expansion.

### API Communication
- **Login/Register**: Uses `axios` with relative URLs (proxied to Flask)
- **All other calls**: Uses native `fetch` with JWT Bearer token from `localStorage`
- **Proxy**: `package.json` has `"proxy": "http://localhost:5000"` for dev
- **Production**: API calls go to `/api/*` which Nginx reverse-proxies to Gunicorn

---

## Key Features by Game Stage

### Submissions Stage
- Submit songs (name, artist, optional comment)
- View your submitted songs
- Delete your submissions
- Owner: access GameSettings (manage dates, songs, players)

### Rankings Stage
- View all songs in randomized order
- Drag songs from "Song Pool" into numbered ranking slots
- Expand/collapse song comments
- Save partial or complete rankings
- Links to auto-generated Spotify/YouTube playlists
- Owner: access GameSettings

### Results Stage
- Table view of all songs sorted by average rank
- Columns: Rank, Song, Artist, Submitted By, Avg, Range, Controversy
- Responsive: collapses to card layout on mobile

---

## Styling Approach

The app uses a **mixed styling strategy**:

1. **Custom CSS** (`styles/index.css`) — Primary stylesheet, ~600 lines. Contains all layout, component, and responsive styles.
2. **Tailwind CSS** — Used minimally (CustomButton.css `@apply`, some inline classes in HomePage).
3. **Bootstrap** — Used for form components (Form, Button from react-bootstrap) in Login/Register.
4. **Custom Font** — "HandFont" (woff2/ttf) gives the hand-drawn notebook aesthetic.
5. **Decorative Images** — Corner images on every container create a "torn paper" frame effect.

### Design Language
- Graph paper background
- Hand-drawn font throughout dashboard
- Sticky note images for menus/popups
- Crumpled paper texture for main popups
- Warm grey (`rgb(64, 57, 43)`) as primary text color
- Red accent for buttons

---

## Known Pain Points & Critical Issues

### Critical
1. **No auth guard on `/dashboard`** — If a user navigates directly to `/dashboard` without a token, the page loads and fails silently on API calls. Should redirect to login.
2. **No token expiry handling** — JWT expires in 1 hour. No refresh mechanism, no graceful redirect on 401. User gets stuck with broken state.
3. **Mixed HTTP libraries** — `axios` for auth, `fetch` for everything else. Inconsistent error handling patterns.

### Code Quality
4. **Dashboard is a god component** — ~350 lines with 15+ state variables, 10+ async functions, and all game logic. Should be split into custom hooks or sub-components.
5. **Dead code** — `GamePopup.js` is unused (superseded by GameDetails). Commented-out code blocks in Dashboard.
6. **Unused dependency** — `react-beautiful-dnd` in package.json but only `@dnd-kit` is used.
7. **`API_BASE_URL` defined but unused for most calls** — Dashboard defines it but most fetch calls use relative `/api/...` paths. The variable is only used for OAuth window.open calls.
8. **No loading states** — No spinners or skeleton UI while fetching games, songs, or rankings.
9. **No error feedback to users** — API failures only log to console. No toast notifications or error messages shown.
10. **Console.log statements everywhere** — Debug logging left in production code.

### UX Issues
11. **No confirmation dialogs** — Deleting songs, removing players, and logging out happen immediately with no confirmation.
12. **No form validation feedback** — Registration doesn't show password mismatch or existing user errors from the backend.
13. **Ranking not auto-saved** — Users must manually click "Save Ranking". Easy to lose work.
14. **Results table sorting is reversed** — `sortedSongs` uses `.reverse()` after sorting by finalRank ascending, which shows worst-ranked first (likely a bug).

### Performance
15. **Unnecessary re-renders** — `useEffect` dependencies like `[selectedGame, showGameSettings, user]` trigger refetches on every state change.
16. **No memoization** — Large lists (songs, rankings) re-render fully on any state change.
17. **Images loaded eagerly** — 8 corner images per component, all loaded immediately.

### Accessibility
18. **No ARIA labels** on interactive elements (game cards, user menu).
19. **Keyboard navigation** not supported for drag-and-drop ranking.
20. **Color contrast** may not meet WCAG standards (grey on graph paper background).

---

## How to Run Locally

### Prerequisites
- Node.js (v18+ recommended, v20 used in CI)
- npm

### Setup
```bash
cd client
npm install
```

### Run Development Server
```bash
npm start
```
Opens at `http://localhost:3000`. Proxies API calls to `http://localhost:5000` (Flask backend must be running).

### Run Tests
```bash
# Single run (no watch mode)
npx react-scripts test --watchAll=false

# Watch mode (interactive)
npm test
```

### Build for Production
```bash
npm run build
```
Output goes to `client/build/`. This is what Nginx serves in production.

---

## How to Deploy to Production

### Build Step
```bash
cd client
npm ci          # Clean install from lockfile
npm run build   # Creates optimized production build
```

### Nginx Configuration (on server)
The production Nginx config serves the React build as static files and proxies `/api` to Gunicorn:

```nginx
server {
    listen 443 ssl;
    server_name rankwebgame.com;

    # SSL certs (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/rankwebgame.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rankwebgame.com/privkey.pem;

    # Serve React build
    root /path/to/RankWebProject/client/build;
    index index.html;

    # SPA fallback — all non-API routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API to Flask/Gunicorn
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Deployment Steps
1. SSH into server
2. `cd /path/to/RankWebProject/client`
3. `git pull origin main`
4. `npm ci && npm run build`
5. Nginx automatically serves the new build (no restart needed for static files)

---

## How to Test in Production

### Smoke Test
1. Navigate to `https://rankwebgame.com` — should see login form
2. Register a new account
3. Login — should redirect to dashboard
4. Verify the graph paper background and hand-drawn font render correctly

### Functional Test
1. **Create a game** — Click "CREATE A RANK", fill in theme and dates, verify game code appears
2. **Join a game** — Click "JOIN A RANK", enter a valid code, verify game appears in grid
3. **Submit songs** — Click a game in submissions stage, submit a song, verify it appears in "Your Submitted Songs"
4. **Rankings** — After stage transition, verify drag-and-drop works, save ranking, reload page, verify ranking persists
5. **Results** — After rank due date passes, verify results table shows statistics

### Cross-Browser / Device Testing
- Test on Chrome, Firefox, Safari
- Test mobile layout (responsive breakpoints at 900px and 700px)
- Verify drag-and-drop works on touch devices (TouchSensor configured)

### Known Test Gaps
- No E2E tests (Cypress, Playwright)
- No visual regression tests
- Frontend unit tests cover only basic rendering (3 test files)
- CI only runs `npm test` — no build verification

---

## CI/CD Pipeline

### Current (GitHub Actions)
```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup Node 20
      - npm ci (client/)
      - npm test (client/)
```

**Limitations:**
- No backend tests
- No build step (doesn't verify production build works)
- No deployment automation
- No linting step

### Recommended Additions
- Add `npm run build` step to verify production build
- Add Python test job for backend
- Add ESLint/Prettier check
- Add deployment step (SSH + build on server)
