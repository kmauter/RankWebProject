"""Webhook server for scheduler callbacks.

Provides an aiohttp web application with a POST /notify endpoint that the
Flask scheduler calls when a game transitions between stages. Validates the
shared secret, extracts game_code and new_stage from the payload, looks up
which servers are tracking the game, and dispatches notifications.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiohttp import web

from bot.config import BOT_NOTIFY_SECRET

if TYPE_CHECKING:
    from bot.api_client import RankWebAPIClient
    from bot.store import ConfigStore

logger = logging.getLogger(__name__)


async def handle_notify(request: web.Request) -> web.Response:
    """Handle POST /notify from the Flask scheduler.

    Body: {"game_code": "ABC123", "new_stage": "rankings", "secret": "..."}

    Returns:
        200 on success
        403 if the secret is invalid
        400 if the payload is malformed (missing game_code or new_stage)
    """
    try:
        payload = await request.json()
    except Exception:
        logger.warning("Received malformed JSON on /notify")
        return web.json_response(
            {"error": "Invalid JSON body"}, status=400
        )

    # Validate secret
    secret = payload.get("secret")
    if not secret or secret != BOT_NOTIFY_SECRET:
        logger.warning("Invalid secret on /notify request")
        return web.json_response(
            {"error": "Forbidden: invalid secret"}, status=403
        )

    # Extract required fields
    game_code = payload.get("game_code")
    new_stage = payload.get("new_stage")

    if not game_code or not new_stage:
        logger.warning(
            "Malformed /notify payload: missing game_code or new_stage"
        )
        return web.json_response(
            {"error": "Bad request: game_code and new_stage are required"},
            status=400,
        )

    # Look up servers tracking this game
    store: ConfigStore = request.app["store"]
    servers = store.get_servers_tracking(game_code)

    if not servers:
        logger.info(
            "No servers tracking game %s, nothing to notify", game_code
        )
        return web.json_response({"status": "ok", "notified": 0})

    # Dispatch notifications to each server
    # The dispatch function is provided by the app context (task 8.2 will
    # flesh out the full implementation with Discord channel sends).
    dispatch = request.app.get("dispatch_notification")
    notified = 0

    if dispatch:
        for server_config in servers:
            try:
                await dispatch(server_config, game_code, new_stage)
                notified += 1
            except Exception:
                logger.exception(
                    "Failed to dispatch notification to server %s for game %s",
                    server_config.server_id,
                    game_code,
                )
    else:
        logger.warning(
            "No dispatch_notification handler registered; "
            "notifications will not be sent."
        )

    logger.info(
        "Processed /notify for game %s -> %s, notified %d server(s)",
        game_code,
        new_stage,
        notified,
    )
    return web.json_response({"status": "ok", "notified": notified})


def create_webhook_app(
    store: ConfigStore,
    api_client: RankWebAPIClient | None = None,
    dispatch_notification=None,
) -> web.Application:
    """Create the aiohttp web application for webhook callbacks.

    Args:
        store: The ConfigStore instance for looking up server tracking.
        api_client: The RankWebAPIClient instance (used by dispatch logic).
        dispatch_notification: Async callable(server_config, game_code, new_stage)
            that sends the actual Discord notification. If None, notifications
            are logged but not sent (placeholder for task 8.2).

    Returns:
        Configured aiohttp web.Application with the /notify route.
    """
    app = web.Application()
    app["store"] = store
    app["api_client"] = api_client
    app["dispatch_notification"] = dispatch_notification
    app.router.add_post("/notify", handle_notify)
    return app
