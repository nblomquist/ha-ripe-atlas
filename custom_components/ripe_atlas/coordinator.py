"""Data update coordinator for RIPE Atlas."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import RipeAtlasApiClient, RipeAtlasProbe
from .const import CONF_PROBE_ID


_LOGGER = logging.getLogger(__name__)


class RipeAtlasDataUpdateCoordinator(DataUpdateCoordinator[dict[int, RipeAtlasProbe]]):
    """Coordinator that polls all configured RIPE Atlas probes."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: RipeAtlasApiClient,
        probes: list[dict[str, int | str]],
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="RIPE Atlas",
            update_interval=timedelta(minutes=5),
        )
        self._client = client
        self._probes = probes

    async def _async_update_data(self) -> dict[int, RipeAtlasProbe]:
        """Fetch data for all configured probes."""
        data: dict[int, RipeAtlasProbe] = {}

        for configured_probe in self._probes:
            probe_id = int(configured_probe[CONF_PROBE_ID])
            data[probe_id] = await self._client.async_get_probe(probe_id)

        return data
