"""RIPE Atlas API client tests."""

from __future__ import annotations

from typing import Any, Self

import aiohttp
import pytest

from custom_components.ripe_atlas.api import (
    RipeAtlasApiClient,
    RipeAtlasApiError,
    RipeAtlasCommunicationError,
    RipeAtlasProbeNotFoundError,
)


class FakeResponse:
    """Minimal aiohttp response test double."""

    def __init__(self, status: int, payload: dict[str, Any]) -> None:
        """Initialize the fake response."""
        self.status = status
        self._payload = payload

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit the async context manager."""

    async def json(self) -> dict[str, Any]:
        """Return the response payload."""
        return self._payload


class FakeSession:
    """Minimal aiohttp client session test double."""

    def __init__(self, response: FakeResponse) -> None:
        """Initialize the fake session."""
        self.response = response
        self.requested_url: str | None = None

    def get(self, url: str) -> FakeResponse:
        """Return the configured fake response."""
        self.requested_url = url
        return self.response


class RaisingSession:
    """Minimal session test double that raises on GET."""

    def get(self, url: str) -> FakeResponse:
        """Raise a client error for transport failure tests."""
        raise aiohttp.ClientError("network unavailable")


async def test_get_probe_returns_normalized_probe_data() -> None:
    """Test fetching one probe returns normalized data."""
    session = FakeSession(
        FakeResponse(
            200,
            {
                "id": 12345,
                "status": {"id": 1, "name": "Connected"},
                "address_v4": "192.0.2.1",
                "address_v6": "2001:db8::1",
                "country_code": "US",
                "firmware_version": "5120-beta",
                "first_connected": 1780320988,
                "last_connected": 1781972686,
                "total_uptime": 1651131,
            },
        )
    )
    client = RipeAtlasApiClient(session)

    probe = await client.async_get_probe(12345)

    assert session.requested_url == "https://atlas.ripe.net/api/v2/probes/12345/"
    assert probe.probe_id == 12345
    assert probe.status_id == 1
    assert probe.total_uptime == 1651131
    assert probe.address_v4 == "192.0.2.1"
    assert probe.address_v6 == "2001:db8::1"
    assert probe.country_code == "US"
    assert probe.firmware_version == "5120-beta"
    assert probe.first_connected == 1780320988
    assert probe.last_connected == 1781972686


async def test_get_probe_maps_404_to_probe_not_found() -> None:
    """Test a missing probe response raises a permanent not-found error."""
    client = RipeAtlasApiClient(FakeSession(FakeResponse(404, {"detail": "Not found"})))

    with pytest.raises(RipeAtlasProbeNotFoundError):
        await client.async_get_probe(12345)


async def test_get_probe_maps_client_error_to_communication_error() -> None:
    """Test transport errors raise communication errors."""
    client = RipeAtlasApiClient(RaisingSession())

    with pytest.raises(RipeAtlasCommunicationError):
        await client.async_get_probe(12345)


async def test_get_probe_maps_malformed_payload_to_api_error() -> None:
    """Test malformed payloads raise API errors."""
    client = RipeAtlasApiClient(FakeSession(FakeResponse(200, {"id": 12345})))

    with pytest.raises(RipeAtlasApiError):
        await client.async_get_probe(12345)
