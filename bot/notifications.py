"""Notification embed formatters for Discord bot messages.

Provides functions for formatting Discord embeds for:
- Stage transition notifications (SUBMIT→RANK, RANK→DONE)
- Deadline reminder notifications
- Results display
- Status and active game displays
"""

from __future__ import annotations

import discord


# Embed colors
COLOR_RANK_OPEN = discord.Color.blue()
COLOR_RESULTS_AVAILABLE = discord.Color.green()
COLOR_DEADLINE_REMINDER = discord.Color.orange()
COLOR_RESULTS = discord.Color.gold()
COLOR_STATUS = discord.Color.blurple()
COLOR_ACTIVE = discord.Color.teal()


def format_rank_open_notification(game_data: dict, role_mention: str) -> discord.Embed:
    """Format the SUBMIT→RANK transition notification embed.

    Includes game title, rank due date, playlist links (if available),
    and pings the Ranker role.

    Validates: Requirements 5.1
    """
    title = game_data.get("title", "Unknown Game")
    rank_due_date = game_data.get("rankDueDate", "N/A")
    spotify_url = game_data.get("spotifyPlaylistUrl")
    youtube_url = game_data.get("youtubePlaylistUrl")

    description = (
        f"**Ranking is now open!** {role_mention}\n\n"
        f"Time to rank the songs for **{title}**.\n"
        f"Rankings are due: **{rank_due_date}**"
    )

    embed = discord.Embed(
        title=f"Ranking Open: {title}",
        description=description,
        color=COLOR_RANK_OPEN,
    )

    # Add playlist links if available
    if spotify_url:
        embed.add_field(name="Spotify Playlist", value=spotify_url, inline=False)
    if youtube_url:
        embed.add_field(name="YouTube Playlist", value=youtube_url, inline=False)

    return embed


def format_results_available_notification(game_data: dict, role_mention: str) -> discord.Embed:
    """Format the RANK→DONE transition notification embed.

    Includes game title and results-available message, pings the Ranker role.

    Validates: Requirements 5.2
    """
    title = game_data.get("title", "Unknown Game")

    description = (
        f"**Results are available!** {role_mention}\n\n"
        f"The rankings for **{title}** are in!\n"
        f"Use `/rank results {game_data.get('gameCode', '')}` to see the results."
    )

    embed = discord.Embed(
        title=f"🎉 Results Available: {title}",
        description=description,
        color=COLOR_RESULTS_AVAILABLE,
    )

    return embed


def format_deadline_reminder(game_data: dict, role_mention: str, deadline_type: str) -> discord.Embed:
    """Format a deadline reminder embed.

    Includes game title and message about the deadline being due tomorrow.
    Pings the Ranker role.

    Args:
        game_data: Game data dict from the Flask API.
        role_mention: The Ranker role mention string (e.g. "<@&123456>").
        deadline_type: Either "submit" or "rank".

    Validates: Requirements 6.1, 6.2
    """
    title = game_data.get("title", "Unknown Game")

    if deadline_type == "submit":
        due_date = game_data.get("submissionDueDate", "N/A")
        action = "Submissions"
    else:
        due_date = game_data.get("rankDueDate", "N/A")
        action = "Rankings"

    description = (
        f"**{action} due tomorrow!** {role_mention}\n\n"
        f"Don't forget — **{action.lower()}** for **{title}** are due **{due_date}**."
    )

    embed = discord.Embed(
        title=f"Deadline Reminder: {title}",
        description=description,
        color=COLOR_DEADLINE_REMINDER,
    )

    return embed


def format_results_embed(game_data: dict, songs: list[dict]) -> discord.Embed:
    """Format the results display embed with ranked songs.

    Shows song rankings with titles, artists, and average rank positions.

    Validates: Requirements 7.1
    """
    title = game_data.get("title", "Unknown Game")

    embed = discord.Embed(
        title=f"Results: {title}",
        description=f"Final rankings for **{title}**:",
        color=COLOR_RESULTS,
    )

    # Sort songs by average rank (lower is better); None values go last
    sorted_songs = sorted(songs, key=lambda s: s.get("averageRank") or float("inf"))

    # Build the results list
    results_lines = []
    for i, song in enumerate(sorted_songs, start=1):
        song_title = song.get("title") or song.get("song_name") or "Unknown"
        artist = song.get("artist", "Unknown")
        avg_rank = song.get("averageRank")
        if avg_rank is not None:
            results_lines.append(f"**#{i}** — {song_title} by {artist} (avg: {avg_rank:.2f})")
        else:
            results_lines.append(f"**#{i}** — {song_title} by {artist} (no rankings)")

    # Discord embed field value limit is 1024 chars, use description for long lists
    results_text = "\n".join(results_lines) if results_lines else "No songs to display."

    embed.add_field(name="Rankings", value=results_text, inline=False)

    return embed


def format_status_embed(games: list[dict]) -> discord.Embed:
    """Format the status display showing all tracked games.

    Shows each game's title, current stage, and relevant due date.

    Validates: Requirements 2.1
    """
    embed = discord.Embed(
        title="Tracked Games Status",
        description="All games currently being tracked in this server:",
        color=COLOR_STATUS,
    )

    if not games:
        embed.description = "No games are currently being tracked."
        return embed

    for game in games:
        game_title = game.get("title", "Unknown Game")
        status = game.get("status", "unknown")
        stage_label = _format_stage_label(status)
        due_date = _get_relevant_due_date(game)

        field_value = f"Stage: {stage_label}\nDue: {due_date}"
        embed.add_field(name=game_title, value=field_value, inline=False)

    return embed


def format_active_embed(games: list[dict]) -> discord.Embed:
    """Format the active games display (SUBMIT/RANK only).

    Shows only games in SUBMIT or RANK stage with title, stage, and due date.

    Validates: Requirements 3.1
    """
    embed = discord.Embed(
        title="🎮 Active Games",
        description="Games currently in progress:",
        color=COLOR_ACTIVE,
    )

    if not games:
        embed.description = "No active games in progress."
        return embed

    for game in games:
        game_title = game.get("title", "Unknown Game")
        status = game.get("status", "unknown")
        stage_label = _format_stage_label(status)
        due_date = _get_relevant_due_date(game)

        field_value = f"Stage: {stage_label}\nDue: {due_date}"
        embed.add_field(name=game_title, value=field_value, inline=False)

    return embed


def _format_stage_label(status: str) -> str:
    """Convert API status string to a user-friendly stage label."""
    labels = {
        "submissions": "📝 Submissions Open",
        "rankings": "🏆 Ranking Open",
        "results": "✅ Complete",
        "done": "✅ Complete",
    }
    return labels.get(status, status.capitalize())


def _get_relevant_due_date(game: dict) -> str:
    """Get the relevant due date based on the game's current stage."""
    status = game.get("status", "")
    if status == "submissions":
        return game.get("submissionDueDate", "N/A")
    elif status == "rankings":
        return game.get("rankDueDate", "N/A")
    else:
        return "—"
