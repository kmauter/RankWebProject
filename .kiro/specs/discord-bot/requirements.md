# Requirements Document

## Introduction

A Discord bot that integrates with the RankWeb application to notify Discord servers about song ranking game activity. The bot supports tracking multiple games per server via slash commands, manages a "Ranker" notification role, and sends automatic notifications when games transition between stages (SUBMIT → RANK → DONE) and when deadlines approach.

## Glossary

- **Bot**: The Discord bot process that connects to Discord's API and responds to slash commands and game events
- **Server**: A Discord server (guild) where the Bot is installed
- **Tracker**: The association between a Server and a Game, including the notification channel and role configuration
- **Game**: A song ranking game managed by the RankWeb Flask application, identified by a unique game_code
- **Stage**: The current phase of a Game — one of SUBMIT, RANK, or DONE
- **Ranker_Role**: A Discord role named "Ranker" used to ping users who want game notifications
- **Notification_Channel**: The Discord text channel where the Bot sends automatic game notifications
- **Flask_API**: The existing RankWeb Flask backend that the Bot calls via HTTP to retrieve game data
- **Scheduler**: The existing APScheduler process in `tasks.py` that detects game stage transitions

## Requirements

### Requirement 1: Game Tracking

**User Story:** As a Discord server member, I want to track RankWeb games in my server, so that the server receives notifications about those games.

#### Acceptance Criteria

1. WHEN a user issues `/rank track <game_code>`, THE Bot SHALL verify the game_code exists by querying the Flask_API and add the Game to the Server's tracked games list
2. IF a user issues `/rank track <game_code>` with a game_code that does not exist in the Flask_API, THEN THE Bot SHALL respond with an error message indicating the game was not found
3. IF a user issues `/rank track <game_code>` for a Game already tracked in the Server, THEN THE Bot SHALL respond with a message indicating the Game is already being tracked
4. WHEN a user issues `/rank untrack <game_code>`, THE Bot SHALL remove the Game from the Server's tracked games list and confirm removal
5. IF a user issues `/rank untrack <game_code>` for a Game not tracked in the Server, THEN THE Bot SHALL respond with an error message indicating the Game is not being tracked
6. THE Bot SHALL support tracking multiple Games simultaneously within a single Server

### Requirement 2: Game Status Display

**User Story:** As a Discord server member, I want to see the status of all tracked games, so that I can quickly check which games are active and their deadlines.

#### Acceptance Criteria

1. WHEN a user issues `/rank status`, THE Bot SHALL display a list of all tracked Games in the Server with each Game's title, current Stage, and relevant due date
2. IF no Games are currently tracked in the Server, THEN THE Bot SHALL respond with a message indicating no games are being tracked

### Requirement 3: Active Games Display

**User Story:** As a Discord server member, I want to see only the games that are still in progress, so that I can focus on games that need my attention.

#### Acceptance Criteria

1. WHEN a user issues `/rank active`, THE Bot SHALL display a list of tracked Games in the Server that are in SUBMIT or RANK Stage, including each Game's title, current Stage, and relevant due date
2. IF no tracked Games in the Server are in SUBMIT or RANK Stage, THEN THE Bot SHALL respond with a message indicating no active games are in progress

### Requirement 4: Ranker Role Assignment

**User Story:** As a Discord server member, I want to opt in to game notifications via a role, so that I only receive pings when I choose to.

#### Acceptance Criteria

1. WHEN a user issues `/rank join`, THE Bot SHALL assign the Ranker_Role to the user
2. WHEN a user issues `/rank join` and a role named "Ranker" already exists in the Server, THE Bot SHALL use the existing role
3. WHEN a user issues `/rank join` and no role named "Ranker" exists in the Server, THE Bot SHALL create the Ranker_Role and assign it to the user
4. WHEN a user issues `/rank leave`, THE Bot SHALL remove the Ranker_Role from the user
5. IF a user issues `/rank leave` and does not have the Ranker_Role, THEN THE Bot SHALL respond with a message indicating the user does not have the role

### Requirement 5: Stage Transition Notifications

**User Story:** As a Ranker role holder, I want to be notified when a tracked game changes stage, so that I know when to rank songs or view results.

#### Acceptance Criteria

1. WHEN a tracked Game transitions from SUBMIT to RANK Stage, THE Bot SHALL send a notification to the Notification_Channel that pings the Ranker_Role and includes the Game title, a message that ranking is open, the rank due date, and playlist links if available
2. WHEN a tracked Game transitions from RANK to DONE Stage, THE Bot SHALL send a notification to the Notification_Channel that pings the Ranker_Role and includes the Game title and a message that results are available
3. THE Bot SHALL receive stage transition events via an HTTP endpoint called by the Scheduler

### Requirement 6: Deadline Reminder Notifications

**User Story:** As a Ranker role holder, I want to be reminded before deadlines, so that I don't forget to submit songs or rank them.

#### Acceptance Criteria

1. WHEN a tracked Game in SUBMIT Stage has a submission deadline within 24 hours, THE Bot SHALL send a reminder notification to the Notification_Channel that pings the Ranker_Role and includes the Game title and a message that submissions are due tomorrow
2. WHEN a tracked Game in RANK Stage has a rank deadline within 24 hours, THE Bot SHALL send a reminder notification to the Notification_Channel that pings the Ranker_Role and includes the Game title and a message that rankings are due tomorrow
3. THE Bot SHALL send each deadline reminder exactly once per Game per deadline

### Requirement 7: Results Display

**User Story:** As a Discord server member, I want to view game results in Discord, so that I can see rankings without opening the web app.

#### Acceptance Criteria

1. WHEN a user issues `/rank results <game_code>` for a tracked Game in DONE Stage, THE Bot SHALL display an embed containing the song rankings with song titles, artists, and average rank positions
2. IF a user issues `/rank results <game_code>` for a Game not in DONE Stage, THEN THE Bot SHALL respond with a message indicating results are not yet available
3. IF a user issues `/rank results <game_code>` for a Game not tracked in the Server, THEN THE Bot SHALL respond with an error message indicating the game is not tracked

### Requirement 8: Notification Channel Configuration

**User Story:** As a server administrator, I want to control which channel receives bot notifications, so that notifications go to the appropriate place.

#### Acceptance Criteria

1. WHEN a user issues `/rank track <game_code>` and no Notification_Channel has been configured for the Server, THE Bot SHALL set the channel where the command was issued as the Notification_Channel
2. WHEN a user issues `/rank channel #channel-name`, THE Bot SHALL update the Notification_Channel for the Server to the specified channel
3. THE Bot SHALL send all automatic notifications (stage transitions and deadline reminders) to the configured Notification_Channel

### Requirement 9: Bot Architecture and Deployment

**User Story:** As a developer, I want the bot to run as a separate process that communicates with the Flask API, so that it can be deployed and scaled independently.

#### Acceptance Criteria

1. THE Bot SHALL run as a separate Python process using the discord.py library
2. THE Bot SHALL retrieve game data by making HTTP requests to the Flask_API
3. THE Bot SHALL store Server tracking configuration (tracked game_codes, notification channel_id, and Ranker_Role role_id) mapped by server_id
4. THE Bot SHALL expose an HTTP endpoint that the Scheduler calls to trigger stage transition notifications
5. THE Bot SHALL be deployable as a systemd service on the production droplet

### Requirement 10: Multi-Server Support

**User Story:** As a bot operator, I want the bot to be invitable to any Discord server, so that multiple communities can use it independently.

#### Acceptance Criteria

1. THE Bot SHALL maintain independent tracking configurations per Server
2. WHEN the same Game is tracked in multiple Servers, THE Bot SHALL send notifications to each Server's Notification_Channel independently
3. THE Bot SHALL register slash commands globally so they are available in all Servers where the Bot is installed
