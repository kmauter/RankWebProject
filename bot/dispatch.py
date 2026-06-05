"""Notification dispatch logic for Discord bot.

Provides the dispatch_notification coroutine that fetches game data from
the API, formats the appropriate notification embed based on stage, and
sends it to the server's configured notification channel with a Ranker
role mention.

Handles errors gracefully: missing channels, deleted channels, and
permission issues are logged and skipped.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord

from bot.notifications import (
    format_rank_open_notification,
    format_results_available_notification,
)

if TYPE_CHECKING:
    from bot.api_client import RankWebAPIClient
    from bot.bot import RankBot
    from bot.store import ServerConfig

logger = logging.getLogger(__name__)


def create_dispatch_notification(
    bot: "RankBot", api_client: "RankWebAPIClient"
):
    """Create a dispatch_notification closure bound to the bot and API client.

    Returns an async callable with signature:
        (server_config: ServerConfig, game_code: str, new_stage: str) -> None

    The returned function:
    1. Fetches game data from the API
    2. Determines the correct embed based on new_stage
    3. Gets the notification channel from the bot
    4. Builds a role mention from server_config.ranker_role_id
    5. Sends the embed + role mention to the channel
    6. Handles errors: channel deleted, bot lacks permissions
    """

    async def dispatch_notification(
        server_config: "ServerConfig", game_code: str, new_stage: str
    ) -> None:
        """Dispatch a stage transition notification to a single server."""
        server_id = server_config.server_id
        channel_id = server_config.notification_channel_id

        # Validate notification channel is configured
        if not channel_id:
            logger.warning(
                "Server %s has no notification channel configured; "
                "skipping notification for game %s",
                server_id,
                game_code,
            )
            return

        # Fetch game data from the API
        game_data = await api_client.get_game(game_code)
        if game_data is None:
            logger.error(
                "Could not fetch game data for %s; "
                "skipping notification to server %s",
                game_code,
                server_id,
            )
            return

        # Determine which embed to format based on the new stage
        role_mention = _build_role_mention(server_config.ranker_role_id)
        embed = _get_notification_embed(game_data, role_mention, new_stage)

        if embed is None:
            logger.warning(
                "Unknown stage '%s' for game %s; skipping notification",
                new_stage,
                game_code,
            )
            return

        # Get the notification channel from the bot
        channel = bot.get_channel(channel_id)
        if channel is None:
            # Channel may have been deleted or bot can't see it
            logger.warning(
                "Notification channel %s not found for server %s; "
                "channel may have been deleted",
                channel_id,
                server_id,
            )
            return

        # Send the notification
        try:
            await channel.send(content=role_mention, embed=embed)
            logger.info(
                "Sent %s notification for game %s to channel %s in server %s",
                new_stage,
                game_code,
                channel_id,
                server_id,
            )
        except discord.Forbidden:
            logger.warning(
                "Bot lacks permission to send messages in channel %s "
                "(server %s); skipping notification for game %s",
                channel_id,
                server_id,
                game_code,
            )
        except discord.NotFound:
            logger.warning(
                "Notification channel %s no longer exists (server %s); "
                "skipping notification for game %s",
                channel_id,
                server_id,
                game_code,
            )
        except discord.HTTPException as exc:
            logger.error(
                "Failed to send notification to channel %s (server %s) "
                "for game %s: %s",
                channel_id,
                server_id,
                game_code,
                exc,
            )

    return dispatch_notification


def _build_role_mention(ranker_role_id: int | None) -> str:
    """Build a Discord role mention string.

    Returns the role mention format (<@&role_id>) if a role ID is configured,
    otherwise returns an empty string.
    """
    if ranker_role_id:
        return f"<@&{ranker_role_id}>"
    return ""


def _get_notification_embed(
    game_data: dict, role_mention: str, new_stage: str
) -> discord.Embed | None:
    """Return the appropriate embed for the given stage transition.

    Args:
        game_data: Game data dict from the Flask API.
        role_mention: The role mention string.
        new_stage: The new stage the game transitioned to.

    Returns:
        A discord.Embed for known stages, or None for unknown stages.
    """
    if new_stage == "rankings":
        return format_rank_open_notification(game_data, role_mention)
    elif new_stage in ("done", "results"):
        return format_results_available_notification(game_data, role_mention)
    else:
        return None
