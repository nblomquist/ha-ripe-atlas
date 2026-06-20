"""Setup and coordinator tests for the RIPE Atlas integration."""

from __future__ import annotations

from typing import Any, Self
from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ripe_atlas.api import RipeAtlasProbe
from custom_components.ripe_atlas.const import CONF_PROBES, DOMAIN


pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


class FakeResponse:
    """Minimal aiohttp response test double."""

    def __init__(self, payload: dict[str, Any], status: int = 200) -> None:
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

    def __init__(self) -> None:
        """Initialize the fake session."""
        self.requested_urls: list[str] = []

    def get(self, url: str) -> FakeResponse:
        """Return a probe payload based on the requested URL."""
        self.requested_urls.append(url)
        probe_id = int(url.rstrip("/").split("/")[-1])
        return FakeResponse(
            {
                "id": probe_id,
                "status": {"id": probe_id % 4},
                "address_v4": "192.0.2.1",
                "address_v6": "2001:db8::1",
                "country_code": "US",
                "firmware_version": "5120-beta",
                "first_connected": 1780320988,
                "last_connected": 1781972686,
                "total_uptime": 1651131,
            }
        )


class NotFoundSession:
    """Minimal session that reports every requested probe as missing."""

    def get(self, url: str) -> FakeResponse:
        """Return a 404 response."""
        return FakeResponse({"detail": "Not found"}, status=404)


async def test_setup_entry_refreshes_all_configured_probes(
    hass: HomeAssistant,
) -> None:
    """Test setup creates coordinator data and status entities for each probe."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PROBES: [
                {"probe_id": 12345, "name": "Home Fiber"},
                {"probe_id": 67890, "name": "Office Probe"},
            ]
        },
    )
    entry.add_to_hass(hass)
    session = FakeSession()

    with patch(
        "custom_components.ripe_atlas.async_get_clientsession",
        return_value=session,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    assert session.requested_urls == [
        "https://atlas.ripe.net/api/v2/probes/12345/",
        "https://atlas.ripe.net/api/v2/probes/67890/",
    ]
    assert coordinator.data == {
        12345: RipeAtlasProbe(
            probe_id=12345,
            status_id=1,
            total_uptime=1651131,
            address_v4="192.0.2.1",
            address_v6="2001:db8::1",
            country_code="US",
            firmware_version="5120-beta",
            first_connected=1780320988,
            last_connected=1781972686,
        ),
        67890: RipeAtlasProbe(
            probe_id=67890,
            status_id=2,
            total_uptime=1651131,
            address_v4="192.0.2.1",
            address_v6="2001:db8::1",
            country_code="US",
            firmware_version="5120-beta",
            first_connected=1780320988,
            last_connected=1781972686,
        ),
    }

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    home_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "12345_status"
    )
    office_entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, "67890_status"
    )

    assert home_entity_id is not None
    assert office_entity_id is not None
    assert hass.states.get(home_entity_id).state == "connected"
    assert hass.states.get(office_entity_id).state == "disconnected"

    home_device = device_registry.async_get_device({(DOMAIN, "12345")})
    office_device = device_registry.async_get_device({(DOMAIN, "67890")})
    assert home_device is not None
    assert office_device is not None
    assert home_device.name == "Home Fiber"
    assert office_device.name == "Office Probe"
    assert entity_registry.async_get(home_entity_id).device_id == home_device.id
    assert entity_registry.async_get(office_entity_id).device_id == office_device.id

    metadata_expectations = {
        "12345_total_uptime": ("1651131", "duration", "s"),
        "12345_address_v4": ("192.0.2.1", None, None),
        "12345_address_v6": ("2001:db8::1", None, None),
        "12345_country_code": ("US", None, None),
        "12345_firmware_version": ("5120-beta", None, None),
        "12345_first_connected": ("2026-06-01T13:36:28+00:00", "timestamp", None),
        "12345_last_connected": ("2026-06-20T16:24:46+00:00", "timestamp", None),
    }
    for unique_id, (state, device_class, unit) in metadata_expectations.items():
        entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, unique_id)
        assert entity_id is not None
        entity_state = hass.states.get(entity_id)
        assert entity_state.state == state
        assert entity_state.attributes.get("device_class") == device_class
        assert entity_state.attributes.get("unit_of_measurement") == unit
        assert entity_registry.async_get(entity_id).device_id == home_device.id


async def test_setup_entry_fails_cleanly_for_missing_probe(
    hass: HomeAssistant,
) -> None:
    """Test a 404 probe response fails setup without creating entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROBES: [{"probe_id": 99999, "name": "Missing Probe"}]},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.ripe_atlas.async_get_clientsession",
        return_value=NotFoundSession(),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is config_entries.ConfigEntryState.SETUP_ERROR
    entity_registry = er.async_get(hass)
    assert entity_registry.async_get_entity_id("sensor", DOMAIN, "99999_status") is None
