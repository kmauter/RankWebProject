"""Deadline detection and active game filtering utilities.

Provides functions for determining when game deadlines are approaching
and filtering games to only those in active (SUBMIT/RANK) stages.
"""

from __future__ import annotations

from datetime import date, timedelta

# Stages considered "active" (games still in progress)
ACTIVE_STAGES = {"submissions", "rankings"}


def is_deadline_approaching(due_date: date, now: date) -> bool:
    """Return True if due_date is within 24 hours (today or tomorrow).

    Specifically, returns True when 0 <= (due_date - now).days <= 1.
    Past deadlines and deadlines more than 1 day away return False.
    """
    delta = due_date - now
    return timedelta(0) <= delta <= timedelta(days=1)


def filter_active_games(games: list[dict]) -> list[dict]:
    """Return only games in SUBMIT or RANK stage.

    Filters the list to include only games whose "status" field
    is in ACTIVE_STAGES ("submissions" or "rankings").
    """
    return [g for g in games if g.get("status") in ACTIVE_STAGES]
