"""Sensor platform for RIPE Atlas."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .const import CONF_PROBE_ID, CONF_PROBE_NAME, CONF_PROBES, DOMAIN
from .coordinator import RipeAtlasDataUpdateCoordinator


STATUS_STATES = {
    0: "never_connected",
    1: "connected",
    2: "disconnected",
    3: "abandoned",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RIPE Atlas sensors from a config entry."""
    coordinator: RipeAtlasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities(
        RipeAtlasProbeStatusSensor(coordinator, configured_probe)
        for configured_probe in entry.data[CONF_PROBES]
    )


class RipeAtlasProbeStatusSensor(
    CoordinatorEntity[RipeAtlasDataUpdateCoordinator], SensorEntity
):
    """Status sensor for one configured RIPE Atlas probe."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    _attr_has_entity_name = True
    _attr_name = "Status"

    def __init__(
        self,
        coordinator: RipeAtlasDataUpdateCoordinator,
        configured_probe: dict[str, int | str],
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self._probe_id = int(configured_probe[CONF_PROBE_ID])
        self._device_name = str(
            configured_probe.get(CONF_PROBE_NAME, f"RIPE Atlas Probe {self._probe_id}")
        )
        self._attr_unique_id = f"{self._probe_id}_status"

    @property
    def native_value(self) -> str | None:
        """Return the lowercase RIPE Atlas probe status."""
        probe = self.coordinator.data.get(self._probe_id)
        if probe is None:
            return None
        return STATUS_STATES.get(probe.status_id)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the Home Assistant device for this probe."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._probe_id))},
            name=self._device_name,
            manufacturer="RIPE Atlas",
            model="Probe",
        )
