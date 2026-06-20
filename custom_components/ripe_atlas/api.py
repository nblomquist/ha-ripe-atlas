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
    total_uptime: int | None
    address_v4: str | None
    address_v6: str | None
    country_code: str | None
    firmware_version: str | None
    first_connected: int | None
    last_connected: int | None


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
                total_uptime=_optional_int(payload.get("total_uptime")),
                address_v4=_optional_str(payload.get("address_v4")),
                address_v6=_optional_str(payload.get("address_v6")),
                country_code=_optional_str(payload.get("country_code")),
                firmware_version=_optional_str(payload.get("firmware_version")),
                first_connected=_optional_int(payload.get("first_connected")),
                last_connected=_optional_int(payload.get("last_connected")),
            )
        except (KeyError, TypeError, ValueError) as err:
            raise RipeAtlasApiError("RIPE Atlas returned malformed probe data") from err


def _optional_int(value: Any) -> int | None:
    """Convert optional RIPE Atlas integer fields."""
    if value is None:
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    """Convert optional RIPE Atlas string fields."""
    if value is None:
        return None
    return str(value)
