"""Entry point for the Discord bot process.

Starts the Discord bot, aiohttp webhook server, and deadline reminder loop
concurrently in the same async event loop. The deadline reminder loop is
started automatically via the bot's setup_hook() when Discord is ready.

Components:
  1. Discord bot (discord.py) — slash commands, role management, notifications
  2. Webhook server (aiohttp) — receives POST /notify from Flask scheduler
  3. Deadline reminder loop (discord.ext.tasks) — periodic deadline checks

Graceful shutdown: Ctrl+C or SIGTERM triggers bot.close() which cancels the
reminder loop and closes the API client, then the webhook runner is cleaned up.
"""

import asyncio
import logging
import sys

from aiohttp import web

from bot.bot import RankBot
from bot.config import BOT_HTTP_PORT, DISCORD_BOT_TOKEN
from bot.dispatch import create_dispatch_notification
from bot.webhook_server import create_webhook_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the Discord bot and webhook server concurrently.

    Startup order:
      1. Webhook server binds to BOT_HTTP_PORT
      2. Discord bot connects (setup_hook syncs commands + starts reminder loop)

    Shutdown order:
      1. Bot closes (cancels reminder loop, closes API client session)
      2. Webhook runner cleans up (stops accepting connections)
    """
    # Validate required configuration before starting
    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN is not set. Cannot start bot.")
        sys.exit(1)

    bot = RankBot()

    # Create the dispatch function bound to the bot and API client
    dispatch_notification = create_dispatch_notification(bot, bot.api_client)

    # Create the webhook app with the bot's shared store and API client.
    app = create_webhook_app(
        store=bot.store,
        api_client=bot.api_client,
        dispatch_notification=dispatch_notification,
    )

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=BOT_HTTP_PORT)

    try:
        await site.start()
        logger.info("Webhook server listening on 0.0.0.0:%s", BOT_HTTP_PORT)
    except OSError as exc:
        logger.error("Failed to start webhook server on port %s: %s", BOT_HTTP_PORT, exc)
        await runner.cleanup()
        sys.exit(1)

    try:
        # Start the bot (this runs until the bot is closed).
        # setup_hook() is called during startup which syncs slash commands
        # and starts the deadline reminder background loop.
        logger.info("Starting Discord bot...")
        async with bot:
            await bot.start(bot.config_token)
    except Exception as exc:
        logger.error("Bot encountered a fatal error: %s", exc)
        raise
    finally:
        await runner.cleanup()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down.")
