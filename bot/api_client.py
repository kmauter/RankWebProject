"""HTTP client for communicating with the Flask API.

Provides async methods to retrieve game details and song data from the
RankWeb Flask backend. Handles connection errors, timeouts, and 404s
gracefully by returning fallback values (None or empty list).
"""

from __future__ import annotations

import logging

import aiohttp

from bot.config import FLASK_API_URL

logger = logging.getLogger(__name__)

# Default timeout for API requests (seconds)
_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class RankWebAPIClient:
    """HTTP client for communicating with the Flask API."""

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or FLASK_API_URL).rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Return the shared session, creating it lazily."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=_REQUEST_TIMEOUT)
        return self._session

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_game(self, game_code: str) -> dict | None:
        """Fetch game details. Returns None if game not found."""
        url = f"{self._base_url}/api/internal/game/{game_code}"
        try:
            session = await self._get_session()
            async with session.get(url) as resp:
                if resp.status == 404:
                    return None
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientConnectionError:
            logger.error("Unable to connect to Flask API at %s", url)
            return None
        except TimeoutError:
            logger.error("Timeout while fetching game %s", game_code)
            return None
        except aiohttp.ClientResponseError as exc:
            logger.error(
                "Unexpected HTTP %s from Flask API for game %s",
                exc.status,
                game_code,
            )
            return None
        except Exception:
            logger.exception("Unexpected error fetching game %s", game_code)
            return None

    async def get_game_songs(self, game_code: str) -> list[dict]:
        """Fetch songs with stats for a game in DONE stage."""
        url = f"{self._base_url}/api/internal/game/{game_code}/songs"
        try:
            session = await self._get_session()
            async with session.get(url) as resp:
                if resp.status == 404:
                    return []
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientConnectionError:
            logger.error("Unable to connect to Flask API at %s", url)
            return []
        except TimeoutError:
            logger.error(
                "Timeout while fetching songs for game %s", game_code
            )
            return []
        except aiohttp.ClientResponseError as exc:
            logger.error(
                "Unexpected HTTP %s from Flask API for game %s songs",
                exc.status,
                game_code,
            )
            return []
        except Exception:
            logger.exception(
                "Unexpected error fetching songs for game %s", game_code
            )
            return []
