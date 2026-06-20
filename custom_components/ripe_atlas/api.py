"""Client for the RIPE Atlas API."""

from __future__ import annotations

from asyncio import TimeoutError as AsyncioTimeoutError
from dataclasses import dataclass
from typing import Any

import aiohttp


ATLAS_API_BASE_URL = "https://atlas.ripe.net/api/v2"


class RipeAtlasError(Exception):
    """Base RIPE Atlas integration error."""


class RipeAtlasApiError(RipeAtlasError):
    """Raised when the RIPE Atlas API returns invalid data or errors."""


class RipeAtlasCommunicationError(RipeAtlasError):
    """Raised when communication with RIPE Atlas fails."""


class RipeAtlasProbeNotFoundError(RipeAtlasError):
    """Raised when RIPE Atlas reports a probe does not exist."""


@dataclass(frozen=True)
class RipeAtlasProbe:
    """Normalized RIPE Atlas probe data used by Home Assistant entities."""

    probe_id: int
    status_id: int


class RipeAtlasApiClient:
    """Minimal RIPE Atlas API client."""

    def __init__(self, session: Any) -> None:
        """Initialize the API client."""
        self._session = session

    async def async_get_probe(self, probe_id: int) -> RipeAtlasProbe:
        """Fetch one public RIPE Atlas probe."""
        try:
            async with self._session.get(
                f"{ATLAS_API_BASE_URL}/probes/{probe_id}/"
            ) as resp:
                if resp.status == 404:
                    raise RipeAtlasProbeNotFoundError(
                        f"RIPE Atlas probe {probe_id} was not found"
                    )
                if resp.status != 200:
                    raise RipeAtlasApiError(
                        f"Unexpected RIPE Atlas status: {resp.status}"
                    )

                payload = await resp.json()
        except (aiohttp.ClientError, AsyncioTimeoutError) as err:
            raise RipeAtlasCommunicationError(
                "Could not communicate with RIPE Atlas"
            ) from err

        try:
            return RipeAtlasProbe(
                probe_id=int(payload["id"]),
                status_id=int(payload["status"]["id"]),
            )
        except (KeyError, TypeError, ValueError) as err:
            raise RipeAtlasApiError("RIPE Atlas returned malformed probe data") from err
