"""Slash command implementations for the /rank command group.

All commands are subcommands of the /rank group registered in bot.py.
"""

from __future__ import annotations

import logging

import discord
from discord import app_commands

from bot.api_client import RankWebAPIClient
from bot.deadline import filter_active_games
from bot.notifications import format_active_embed, format_results_embed, format_status_embed
from bot.store import ConfigStore

logger = logging.getLogger(__name__)

# Shared instances — initialized when commands are registered
_store: ConfigStore | None = None
_api_client: RankWebAPIClient | None = None

RANKER_ROLE_NAME = "Ranker"


async def _tracked_games_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete for game_code parameters — shows tracked games with titles.

    Fetches game titles from the API for the server's tracked games,
    then filters by what the user has typed so far.
    """
    assert _store is not None
    assert _api_client is not None

    server_id = interaction.guild_id
    if server_id is None:
        return []

    config = _store.get_config(server_id)
    if not config.tracked_games:
        return []

    choices: list[app_commands.Choice[str]] = []
    for game_code in list(config.tracked_games)[:25]:  # Discord max 25 choices
        # Try to get the title from the API (cached in practice)
        game_data = await _api_client.get_game(game_code)
        if game_data:
            title = game_data.get("title", game_code)
            label = f"{title} ({game_code})"
        else:
            label = game_code

        # Filter by what the user has typed
        if current.lower() in label.lower() or current.lower() in game_code.lower():
            choices.append(app_commands.Choice(name=label[:100], value=game_code))

    return choices


def register_commands(
    group: app_commands.Group,
    store: ConfigStore,
    api_client: RankWebAPIClient,
) -> None:
    """Register all /rank subcommands on the given command group.

    Args:
        group: The /rank app_commands.Group to attach commands to.
        store: The ConfigStore instance for server configuration.
        api_client: The RankWebAPIClient for Flask API communication.
    """
    global _store, _api_client
    _store = store
    _api_client = api_client

    group.add_command(_track_command)
    group.add_command(_untrack_command)
    group.add_command(_join_command)
    group.add_command(_leave_command)
    group.add_command(_results_command)
    group.add_command(_status_command)
    group.add_command(_active_command)
    group.add_command(_channel_command)


@app_commands.command(name="track", description="Track a RankWeb game in this server")
@app_commands.describe(game_code="The game code to track")
async def _track_command(interaction: discord.Interaction, game_code: str) -> None:
    """Track a game in this server.

    Validates the game_code against the Flask API, adds it to the server's
    tracked games, and sets the notification channel if not already configured.

    Validates: Requirements 1.1, 1.2, 1.3, 1.6, 8.1
    """
    assert _store is not None
    assert _api_client is not None

    server_id = interaction.guild_id
    if server_id is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True,
        )
        return

    # Requirement 1.3: Check if already tracked
    config = _store.get_config(server_id)
    if game_code in config.tracked_games:
        await interaction.response.send_message(
            f"Game `{game_code}` is already being tracked in this server.",
            ephemeral=True,
        )
        return

    # Requirements 1.1, 1.2: Verify game exists via API
    game_data = await _api_client.get_game(game_code)
    if game_data is None:
        await interaction.response.send_message(
            f"Game `{game_code}` was not found. Please check the game code and try again.",
            ephemeral=True,
        )
        return

    # Requirement 1.1, 1.6: Add to tracked games
    _store.track_game(server_id, game_code)

    # Requirement 8.1: Set notification channel if not configured
    if config.notification_channel_id is None:
        _store.set_channel(server_id, interaction.channel_id)

    _store.save()

    game_title = game_data.get("title", game_code)
    await interaction.response.send_message(
        f"Now tracking **{game_title}** (`{game_code}`) in this server."
    )


@app_commands.command(name="untrack", description="Stop tracking a RankWeb game in this server")
@app_commands.describe(game_code="The game code to stop tracking")
@app_commands.autocomplete(game_code=_tracked_games_autocomplete)
async def _untrack_command(interaction: discord.Interaction, game_code: str) -> None:
    """Stop tracking a game in this server.

    Validates: Requirements 1.4, 1.5
    """
    assert _store is not None

    server_id = interaction.guild_id
    if server_id is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True,
        )
        return

    # Requirements 1.4, 1.5: Remove from tracked games
    removed = _store.untrack_game(server_id, game_code)
    if not removed:
        await interaction.response.send_message(
            f"Game `{game_code}` is not being tracked in this server.",
            ephemeral=True,
        )
        return

    _store.save()

    await interaction.response.send_message(
        f"Stopped tracking game `{game_code}` in this server."
    )


@app_commands.command(name="join", description="Get the Ranker role to receive game notifications")
async def _join_command(interaction: discord.Interaction) -> None:
    """Assign the Ranker role to the user.

    If a "Ranker" role already exists in the server, uses the existing role.
    If no "Ranker" role exists, creates one and assigns it to the user.
    Stores the role_id in the server config for future reference.

    Validates: Requirements 4.1, 4.2, 4.3
    """
    assert _store is not None

    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.", ephemeral=True
        )
        return

    member = interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message(
            "Unable to determine your server membership.", ephemeral=True
        )
        return

    # Find existing "Ranker" role or create one (Req 4.2, 4.3)
    ranker_role = discord.utils.get(guild.roles, name=RANKER_ROLE_NAME)

    try:
        if ranker_role is None:
            # Requirement 4.3: Create the Ranker role
            ranker_role = await guild.create_role(
                name=RANKER_ROLE_NAME,
                reason="Created by RankBot for game notifications",
            )
            logger.info(
                "Created Ranker role (ID: %s) in guild %s",
                ranker_role.id,
                guild.id,
            )

        # Check if user already has the role
        if ranker_role in member.roles:
            await interaction.response.send_message(
                f"You already have the **{RANKER_ROLE_NAME}** role! "
                "You'll receive game notifications.",
                ephemeral=True,
            )
            return

        # Requirement 4.1: Assign the role to the user
        await member.add_roles(
            ranker_role, reason="User requested Ranker role via /rank join"
        )

        # Store the role_id in config
        _store.set_role(guild.id, ranker_role.id)
        _store.save()

        await interaction.response.send_message(
            f"You've been given the **{RANKER_ROLE_NAME}** role! "
            "You'll now receive game notifications.",
            ephemeral=True,
        )

    except discord.Forbidden:
        logger.warning(
            "Missing Manage Roles permission in guild %s", guild.id
        )
        await interaction.response.send_message(
            "I need the **Manage Roles** permission to assign the Ranker role. "
            "Please ask a server admin to grant me this permission.",
            ephemeral=True,
        )
    except discord.HTTPException as exc:
        logger.error(
            "Failed to assign Ranker role in guild %s: %s", guild.id, exc
        )
        await interaction.response.send_message(
            "Something went wrong while assigning the role. Please try again later.",
            ephemeral=True,
        )


@app_commands.command(name="leave", description="Remove the Ranker role to stop game notifications")
async def _leave_command(interaction: discord.Interaction) -> None:
    """Remove the Ranker role from the user.

    If the user doesn't have the Ranker role, responds with an error message.

    Validates: Requirements 4.4, 4.5
    """
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.", ephemeral=True
        )
        return

    member = interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message(
            "Unable to determine your server membership.", ephemeral=True
        )
        return

    # Find the Ranker role in the guild
    ranker_role = discord.utils.get(guild.roles, name=RANKER_ROLE_NAME)

    # Requirement 4.5: If user doesn't have the role, respond with error
    if ranker_role is None or ranker_role not in member.roles:
        await interaction.response.send_message(
            f"You don't have the **{RANKER_ROLE_NAME}** role.",
            ephemeral=True,
        )
        return

    try:
        # Requirement 4.4: Remove the Ranker role from the user
        await member.remove_roles(
            ranker_role, reason="User requested role removal via /rank leave"
        )
        await interaction.response.send_message(
            f"The **{RANKER_ROLE_NAME}** role has been removed. "
            "You'll no longer receive game notifications.",
            ephemeral=True,
        )

    except discord.Forbidden:
        logger.warning(
            "Missing Manage Roles permission in guild %s", guild.id
        )
        await interaction.response.send_message(
            "I need the **Manage Roles** permission to remove the Ranker role. "
            "Please ask a server admin to grant me this permission.",
            ephemeral=True,
        )
    except discord.HTTPException as exc:
        logger.error(
            "Failed to remove Ranker role in guild %s: %s", guild.id, exc
        )
        await interaction.response.send_message(
            "Something went wrong while removing the role. Please try again later.",
            ephemeral=True,
        )


@app_commands.command(name="results", description="Show results for a completed game")
@app_commands.describe(game_code="The game code to show results for")
@app_commands.autocomplete(game_code=_tracked_games_autocomplete)
async def _results_command(interaction: discord.Interaction, game_code: str) -> None:
    """Show results for a tracked game that is in DONE stage.

    Validates: Requirements 7.1, 7.2, 7.3
    """
    assert _store is not None
    assert _api_client is not None

    server_id = interaction.guild_id
    if server_id is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True,
        )
        return

    # Requirement 7.3: Check if game is tracked in this server
    config = _store.get_config(server_id)
    if game_code not in config.tracked_games:
        await interaction.response.send_message(
            f"Game `{game_code}` is not tracked in this server. "
            f"Use `/rank track {game_code}` to start tracking it.",
            ephemeral=True,
        )
        return

    # Fetch game data from API
    game_data = await _api_client.get_game(game_code)
    if game_data is None:
        await interaction.response.send_message(
            "Unable to reach the game server. Please try again later.",
            ephemeral=True,
        )
        return

    # Requirement 7.2: Verify game is in DONE stage
    status = game_data.get("status", "")
    if status != "results":
        await interaction.response.send_message(
            f"Results for `{game_code}` are not yet available. "
            f"The game is currently in the **{status}** stage.",
            ephemeral=True,
        )
        return

    # Requirement 7.1: Fetch songs and display results embed
    songs = await _api_client.get_game_songs(game_code)
    if not songs:
        await interaction.response.send_message(
            f"No song data found for game `{game_code}`.",
            ephemeral=True,
        )
        return

    embed = format_results_embed(game_data, songs)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="status", description="Show all tracked games and their status")
async def _status_command(interaction: discord.Interaction) -> None:
    """Fetch all tracked games from API and display their status.

    Validates: Requirements 2.1, 2.2
    """
    assert _store is not None
    assert _api_client is not None

    server_id = interaction.guild_id
    if server_id is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True,
        )
        return

    config = _store.get_config(server_id)

    # Requirement 2.2: If no games tracked, respond accordingly
    if not config.tracked_games:
        await interaction.response.send_message(
            "No games are currently being tracked in this server. "
            "Use `/rank track <game_code>` to start tracking a game.",
            ephemeral=True,
        )
        return

    # Defer since we may need multiple API calls
    await interaction.response.defer()

    # Fetch game data for all tracked games
    games: list[dict] = []
    for game_code in config.tracked_games:
        game_data = await _api_client.get_game(game_code)
        if game_data is not None:
            games.append(game_data)

    if not games:
        await interaction.followup.send(
            "Unable to fetch game data. The game server may be unavailable. "
            "Try again later.",
        )
        return

    # Requirement 2.1: Display all tracked games with title, stage, due date
    embed = format_status_embed(games)
    await interaction.followup.send(embed=embed)


@app_commands.command(name="active", description="Show games currently in progress")
async def _active_command(interaction: discord.Interaction) -> None:
    """Fetch tracked games, filter to active ones (SUBMIT/RANK), and display.

    Validates: Requirements 3.1, 3.2
    """
    assert _store is not None
    assert _api_client is not None

    server_id = interaction.guild_id
    if server_id is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True,
        )
        return

    config = _store.get_config(server_id)

    if not config.tracked_games:
        await interaction.response.send_message(
            "No games are currently being tracked in this server. "
            "Use `/rank track <game_code>` to start tracking a game.",
            ephemeral=True,
        )
        return

    # Defer since we may need multiple API calls
    await interaction.response.defer()

    # Fetch game data for all tracked games
    games: list[dict] = []
    for game_code in config.tracked_games:
        game_data = await _api_client.get_game(game_code)
        if game_data is not None:
            games.append(game_data)

    if not games:
        await interaction.followup.send(
            "Unable to fetch game data. The game server may be unavailable. "
            "Try again later.",
        )
        return

    # Requirement 3.1: Filter to only active games (SUBMIT/RANK stages)
    active_games = filter_active_games(games)

    # Requirement 3.2: If no active games, respond accordingly
    if not active_games:
        await interaction.followup.send(
            "No active games in progress. All tracked games are complete.",
        )
        return

    embed = format_active_embed(active_games)
    await interaction.followup.send(embed=embed)


@app_commands.command(name="channel", description="Set the notification channel for bot alerts")
@app_commands.describe(channel="The text channel to send notifications to")
async def _channel_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
) -> None:
    """Set the notification channel for this server.

    Updates the server's notification channel in the config store
    so all automatic notifications (stage transitions, deadline reminders)
    are sent to the specified channel.

    Validates: Requirements 8.2, 8.3
    """
    assert _store is not None

    server_id = interaction.guild_id
    if server_id is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True,
        )
        return

    _store.set_channel(server_id, channel.id)
    _store.save()

    await interaction.response.send_message(
        f"Notification channel updated to {channel.mention}. "
        f"All automatic notifications will be sent there.",
    )
    logger.info(
        "Server %s set notification channel to %s (%s)",
        server_id,
        channel.name,
        channel.id,
    )
