# Implementation Plan: Discord Bot

## Overview

Implement a Discord bot as a standalone Python process that integrates with the existing RankWeb Flask API. The bot uses `discord.py` for slash commands and Discord interaction, `aiohttp` for HTTP client/server communication, and a JSON file store for per-server configuration. The bot enables game tracking, automatic stage transition notifications, deadline reminders, and in-Discord results display.

## Tasks

- [x] 1. Set up bot project structure and configuration
  - [x] 1.1 Create bot module directory and configuration
    - Create `bot/` directory with `__init__.py`
    - Create `bot/config.py` that reads `DISCORD_BOT_TOKEN`, `BOT_NOTIFY_SECRET`, `FLASK_API_URL`, and `BOT_HTTP_PORT` from environment variables (shared `.env` file)
    - Add `discord.py` and `aiohttp` to project dependencies
    - _Requirements: 9.1, 9.5_

  - [X] 1.2 Create bot entry point and client setup
    - Create `bot/main.py` with async entry point that starts both the Discord bot and the aiohttp webhook server concurrently
    - Create `bot/bot.py` with the Discord client class extending `commands.Bot`, registering the `/rank` command group
    - _Requirements: 9.1, 10.3_

- [x] 2. Implement server configuration store
  - [x] 2.1 Implement ConfigStore and ServerConfig data model
    - Create `bot/store.py` with `ServerConfig` dataclass (server_id, tracked_games set, notification_channel_id, ranker_role_id, reminders_sent set)
    - Implement `ConfigStore` class with methods: `get_config`, `track_game`, `untrack_game`, `set_channel`, `set_role`, `mark_reminder_sent`, `is_reminder_sent`, `get_servers_tracking`, `save`, `load`
    - Persist to JSON file at configurable path (default `bot/data/config.json`)
    - _Requirements: 9.3, 10.1, 1.6_

  - [ ]* 2.2 Write property test for track/untrack set semantics
    - **Property 1: Track/Untrack Set Semantics**
    - **Validates: Requirements 1.1, 1.3, 1.4, 1.5, 1.6**

  - [ ]* 2.3 Write property test for server config round-trip serialization
    - **Property 8: Server Config Round-Trip**
    - **Validates: Requirements 9.3**

  - [ ]* 2.4 Write property test for reminder deduplication
    - **Property 6: Reminder Deduplication**
    - **Validates: Requirements 6.3**

- [x] 3. Implement Flask API client
  - [x] 3.1 Implement RankWebAPIClient
    - Create `bot/api_client.py` with `RankWebAPIClient` class
    - Implement `get_game(game_code)` method that GETs `/api/game/<game_code>` and returns dict or None
    - Implement `get_game_songs(game_code)` method that GETs `/api/game/<game_code>/songs` and returns list of song dicts
    - Handle connection errors, 404s, and timeouts gracefully
    - _Requirements: 9.2, 1.1, 1.2, 7.1_

  - [ ]* 3.2 Write unit tests for API client
    - Test successful game retrieval (200 response)
    - Test game not found (404 response returns None)
    - Test connection error handling
    - _Requirements: 9.2_

- [x] 4. Implement notification formatting
  - [x] 4.1 Implement notification embed formatters
    - Create `bot/notifications.py` with functions: `format_rank_open_notification`, `format_results_available_notification`, `format_deadline_reminder`, `format_results_embed`, `format_status_embed`, `format_active_embed`
    - Each function returns a `discord.Embed` with appropriate title, description, color, and fields
    - Include game title, due dates, playlist links (when available), and role mentions as specified
    - _Requirements: 5.1, 5.2, 6.1, 6.2, 2.1, 3.1, 7.1_

  - [ ]* 4.2 Write property test for stage transition notification completeness
    - **Property 4: Stage Transition Notification Completeness**
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 4.3 Write property test for results embed completeness
    - **Property 7: Results Embed Completeness**
    - **Validates: Requirements 7.1**

  - [ ]* 4.4 Write property test for status display completeness
    - **Property 3: Status Display Completeness**
    - **Validates: Requirements 2.1**

- [x] 5. Implement deadline detection logic
  - [x] 5.1 Implement deadline proximity detection
    - Add `is_deadline_approaching(due_date, now)` function (in `bot/notifications.py` or a utility module)
    - Returns True if `0 <= (due_date - now).days <= 1`
    - Implement `filter_active_games(games)` function that filters for SUBMIT/RANK stages
    - _Requirements: 6.1, 6.2, 3.1_

  - [ ]* 5.2 Write property test for deadline proximity detection
    - **Property 5: Deadline Proximity Detection**
    - **Validates: Requirements 6.1, 6.2**

  - [ ]* 5.3 Write property test for active games filter correctness
    - **Property 2: Active Games Filter Correctness**
    - **Validates: Requirements 3.1**

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement slash commands
  - [x] 7.1 Implement `/rank track` and `/rank untrack` commands
    - Create `bot/commands.py` with command group registered under `/rank`
    - Implement `track` subcommand: validate game_code via API client, add to store, set notification channel if not configured, respond with confirmation or error
    - Implement `untrack` subcommand: remove from store, respond with confirmation or error
    - Use ephemeral responses for error messages
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 8.1_

  - [x] 7.2 Implement `/rank status` and `/rank active` commands
    - Implement `status` subcommand: fetch all tracked games from API, format with `format_status_embed`, handle empty state
    - Implement `active` subcommand: fetch tracked games, filter active, format with `format_active_embed`, handle empty state
    - _Requirements: 2.1, 2.2, 3.1, 3.2_

  - [x] 7.3 Implement `/rank join` and `/rank leave` commands
    - Implement `join` subcommand: find or create "Ranker" role, assign to user, store role_id in config
    - Implement `leave` subcommand: remove "Ranker" role from user, handle case where user doesn't have role
    - Handle missing Manage Roles permission gracefully
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 7.4 Implement `/rank results` command
    - Implement `results` subcommand: verify game is tracked, verify game is in DONE stage, fetch songs from API, format with `format_results_embed`
    - Handle errors: not tracked, not done, API errors
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 7.5 Implement `/rank channel` command
    - Implement `channel` subcommand: accept a TextChannel parameter, update notification channel in store, respond with confirmation
    - _Requirements: 8.2, 8.3_

  - [ ]* 7.6 Write unit tests for slash commands
    - Test each command's success and error paths with mocked API client and ConfigStore
    - Test track with valid/invalid/duplicate game_codes
    - Test status/active with empty and populated game lists
    - Test join/leave role assignment logic
    - Test results with valid/invalid/not-done games
    - _Requirements: 1.1-1.6, 2.1-2.2, 3.1-3.2, 4.1-4.5, 7.1-7.3, 8.1-8.2_

- [x] 8. Implement webhook server and notification dispatch
  - [x] 8.1 Implement webhook server for scheduler callbacks
    - Create `bot/webhook_server.py` with aiohttp web application
    - Implement `POST /notify` endpoint that validates the shared secret, extracts game_code and new_stage from payload
    - Return 403 for invalid secret, 400 for malformed payload
    - On valid request: look up servers tracking the game_code, send notification to each server's notification channel
    - _Requirements: 5.3, 9.4_

  - [x] 8.2 Implement notification dispatch logic
    - In webhook handler or notifications module: for each server tracking the game, fetch game data from API, format the appropriate notification embed, send to the server's notification channel with Ranker role mention
    - Handle cases where notification channel is deleted or bot lacks send permission
    - _Requirements: 5.1, 5.2, 10.1, 10.2_

  - [ ]* 8.3 Write property test for multi-server notification dispatch
    - **Property 9: Multi-Server Notification Dispatch**
    - **Validates: Requirements 10.1, 10.2**

  - [ ]* 8.4 Write unit tests for webhook endpoint
    - Test valid payload with correct secret triggers notification
    - Test invalid secret returns 403
    - Test malformed payload returns 400
    - _Requirements: 5.3, 9.4_

- [x] 9. Implement deadline reminder loop
  - [x] 9.1 Implement periodic deadline reminder checking
    - Add a background task loop in the bot (using `discord.ext.tasks`) that runs every few hours
    - For each server's tracked games: fetch game data, check if deadline is approaching, check if reminder already sent (dedup via store), send reminder notification if needed, mark as sent
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 10. Wire everything together and integrate with Flask scheduler
  - [x] 10.1 Wire bot startup to launch all components
    - Update `bot/main.py` to start the Discord bot, webhook server, and deadline reminder loop concurrently
    - Ensure graceful shutdown of all components
    - _Requirements: 9.1, 9.4, 9.5_

  - [x] 10.2 Add webhook call to Flask scheduler
    - Modify `app/tasks.py` to POST to the bot's `/notify` endpoint when a game stage transition is detected
    - Include `game_code`, `new_stage`, and `secret` in the payload
    - Add `BOT_NOTIFY_URL` and `BOT_NOTIFY_SECRET` to the Flask app's config
    - _Requirements: 5.3, 9.4_

  - [x] 10.3 Create systemd service file and deployment config
    - Create `rankbot.service` systemd unit file for running the bot as a service
    - Document environment variable requirements in `.env.example`
    - _Requirements: 9.5_

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The bot uses Python with `discord.py` v2.x, `aiohttp`, and `pytest` for testing
- All slash commands are ephemeral for error responses to avoid channel clutter

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "2.4", "3.1", "5.1"] },
    { "id": 3, "tasks": ["3.2", "4.1", "5.2", "5.3"] },
    { "id": 4, "tasks": ["4.2", "4.3", "4.4", "7.1", "7.2", "7.3", "7.4", "7.5"] },
    { "id": 5, "tasks": ["7.6", "8.1"] },
    { "id": 6, "tasks": ["8.2", "8.3", "8.4", "9.1"] },
    { "id": 7, "tasks": ["10.1", "10.2"] },
    { "id": 8, "tasks": ["10.3"] }
  ]
}
```
