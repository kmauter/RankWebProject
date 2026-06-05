"""Discord bot client setup and command tree."""

from __future__ import annotations

import logging
from datetime import date, datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot.api_client import RankWebAPIClient
from bot.commands import register_commands
from bot.config import DISCORD_BOT_TOKEN
from bot.deadline import is_deadline_approaching
from bot.notifications import format_deadline_reminder
from bot.store import ConfigStore

logger = logging.getLogger(__name__)


class RankBot(commands.Bot):
    """Discord bot client for RankWeb game notifications."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True

        super().__init__(
            command_prefix="!",  # Not used, but required by commands.Bot
            intents=intents,
        )

        # Initialize shared dependencies
        self.store = ConfigStore()
        self.store.load()
        self.api_client = RankWebAPIClient()

        # Register the /rank command group
        self.rank_group = app_commands.Group(
            name="rank",
            description="RankWeb game tracking commands",
        )
        self.tree.add_command(self.rank_group)

        # Register subcommands on the rank group
        register_commands(self.rank_group, self.store, self.api_client)

    async def setup_hook(self) -> None:
        """Called when the bot is starting up. Sync commands globally."""
        # Set up global error handler for slash commands
        self.tree.on_error = self._on_app_command_error

        await self.tree.sync()
        logger.info("Slash commands synced globally.")

        # Start the deadline reminder background loop
        self.check_deadline_reminders.start()
        logger.info("Deadline reminder loop started.")

    async def _on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Global error handler for all slash commands."""
        # Unwrap the CommandInvokeError to get the original exception
        original = error.__cause__ if error.__cause__ else error
        logger.error(
            "Unhandled error in command '%s': %s",
            interaction.command.name if interaction.command else "unknown",
            original,
            exc_info=original,
        )

        message = "Something went wrong. Please try again later."

        # Try to respond to the user
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            pass

    async def on_ready(self) -> None:
        """Called when the bot has connected to Discord."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")

    async def close(self) -> None:
        """Clean up resources on shutdown."""
        self.check_deadline_reminders.cancel()
        await self.api_client.close()
        await super().close()

    @property
    def config_token(self) -> str:
        """Return the configured bot token."""
        return DISCORD_BOT_TOKEN

    def run_bot(self) -> None:
        """Start the bot with the configured token."""
        self.run(DISCORD_BOT_TOKEN, log_handler=None)

    @tasks.loop(hours=4)
    async def check_deadline_reminders(self) -> None:
        """Periodic task that checks for approaching deadlines and sends reminders.

        Runs every 4 hours. For each server's tracked games, fetches game data
        from the API, checks if a deadline is approaching, deduplicates via the
        store, and sends a reminder notification if needed.

        Requirements: 6.1, 6.2, 6.3
        """
        logger.info("Running deadline reminder check...")
        today = date.today()

        # Iterate over all server configs in the store
        for server_id, config in list(self.store._configs.items()):
            if not config.tracked_games:
                continue

            # Determine notification channel
            channel_id = config.notification_channel_id
            if channel_id is None:
                continue

            channel = self.get_channel(channel_id)
            if channel is None:
                logger.warning(
                    "Notification channel %s not found for server %s, skipping.",
                    channel_id,
                    server_id,
                )
                continue

            # Determine role mention
            role_mention = ""
            if config.ranker_role_id:
                role_mention = f"<@&{config.ranker_role_id}>"

            for game_code in list(config.tracked_games):
                await self._check_game_deadline(
                    server_id, game_code, channel, role_mention, today
                )

        # Persist any newly-marked reminders
        self.store.save()
        logger.info("Deadline reminder check complete.")

    @check_deadline_reminders.before_loop
    async def _before_deadline_check(self) -> None:
        """Wait until the bot is ready before starting the reminder loop."""
        await self.wait_until_ready()

    async def _check_game_deadline(
        self,
        server_id: int,
        game_code: str,
        channel: discord.abc.Messageable,
        role_mention: str,
        today: date,
    ) -> None:
        """Check a single game for approaching deadlines and send a reminder if needed."""
        game_data = await self.api_client.get_game(game_code)
        if game_data is None:
            logger.debug("Could not fetch game %s, skipping.", game_code)
            return

        status = game_data.get("status", "")

        # Check submission deadline for games in SUBMIT stage
        if status == "submissions":
            due_date_str = game_data.get("submissionDueDate")
            if due_date_str:
                await self._maybe_send_reminder(
                    server_id, game_code, game_data, due_date_str,
                    "submit", channel, role_mention, today,
                )

        # Check rank deadline for games in RANK stage
        elif status == "rankings":
            due_date_str = game_data.get("rankDueDate")
            if due_date_str:
                await self._maybe_send_reminder(
                    server_id, game_code, game_data, due_date_str,
                    "rank", channel, role_mention, today,
                )

    async def _maybe_send_reminder(
        self,
        server_id: int,
        game_code: str,
        game_data: dict,
        due_date_str: str,
        deadline_type: str,
        channel: discord.abc.Messageable,
        role_mention: str,
        today: date,
    ) -> None:
        """Parse the due date, check proximity and dedup, then send if needed."""
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            logger.warning(
                "Invalid due date '%s' for game %s, skipping.",
                due_date_str,
                game_code,
            )
            return

        if not is_deadline_approaching(due_date, today):
            return

        # Deduplication check
        if self.store.is_reminder_sent(server_id, game_code, deadline_type):
            return

        # Send the reminder
        embed = format_deadline_reminder(game_data, role_mention, deadline_type)
        try:
            content = role_mention if role_mention else None
            await channel.send(content=content, embed=embed)
            self.store.mark_reminder_sent(server_id, game_code, deadline_type)
            logger.info(
                "Sent %s deadline reminder for game %s in server %s.",
                deadline_type,
                game_code,
                server_id,
            )
        except discord.Forbidden:
            logger.warning(
                "Missing permissions to send reminder in channel %s for server %s.",
                channel.id if hasattr(channel, "id") else "unknown",
                server_id,
            )
        except discord.HTTPException as exc:
            logger.error(
                "Failed to send reminder for game %s in server %s: %s",
                game_code,
                server_id,
                exc,
            )
