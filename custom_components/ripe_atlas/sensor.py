"""Sensor platform for RIPE Atlas."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import RipeAtlasProbe
from .const import CONF_PROBE_ID, CONF_PROBE_NAME, CONF_PROBES, DOMAIN
from .coordinator import RipeAtlasDataUpdateCoordinator


STATUS_STATES = {
    0: "never_connected",
    1: "connected",
    2: "disconnected",
    3: "abandoned",
}


@dataclass(frozen=True, kw_only=True)
class RipeAtlasProbeSensorDescription(SensorEntityDescription):
    """Description for one RIPE Atlas probe sensor."""

    key: str
    value_fn: Callable[[RipeAtlasProbe], str | int | datetime | None]


METADATA_SENSOR_DESCRIPTIONS = (
    RipeAtlasProbeSensorDescription(
        key="total_uptime",
        name="Total uptime",
        value_fn=lambda probe: probe.total_uptime,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    RipeAtlasProbeSensorDescription(
        key="address_v4",
        name="IPv4 address",
        value_fn=lambda probe: probe.address_v4,
    ),
    RipeAtlasProbeSensorDescription(
        key="address_v6",
        name="IPv6 address",
        value_fn=lambda probe: probe.address_v6,
    ),
    RipeAtlasProbeSensorDescription(
        key="country_code",
        name="Country code",
        value_fn=lambda probe: probe.country_code,
    ),
    RipeAtlasProbeSensorDescription(
        key="firmware_version",
        name="Firmware version",
        value_fn=lambda probe: probe.firmware_version,
    ),
    RipeAtlasProbeSensorDescription(
        key="first_connected",
        name="First connected",
        value_fn=lambda probe: _timestamp_to_datetime(probe.first_connected),
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    RipeAtlasProbeSensorDescription(
        key="last_connected",
        name="Last connected",
        value_fn=lambda probe: _timestamp_to_datetime(probe.last_connected),
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RIPE Atlas sensors from a config entry."""
    coordinator: RipeAtlasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    entities: list[SensorEntity] = []
    for configured_probe in entry.data[CONF_PROBES]:
        entities.append(RipeAtlasProbeStatusSensor(coordinator, configured_probe))
        entities.extend(
            RipeAtlasProbeMetadataSensor(coordinator, configured_probe, description)
            for description in METADATA_SENSOR_DESCRIPTIONS
        )

    async_add_entities(entities)


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


class RipeAtlasProbeMetadataSensor(
    CoordinatorEntity[RipeAtlasDataUpdateCoordinator], SensorEntity
):
    """Metadata sensor for one configured RIPE Atlas probe."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RipeAtlasDataUpdateCoordinator,
        configured_probe: dict[str, int | str],
        description: RipeAtlasProbeSensorDescription,
    ) -> None:
        """Initialize the metadata sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._probe_id = int(configured_probe[CONF_PROBE_ID])
        self._device_name = str(
            configured_probe.get(CONF_PROBE_NAME, f"RIPE Atlas Probe {self._probe_id}")
        )
        self._attr_name = description.name
        self._attr_unique_id = f"{self._probe_id}_{description.key}"
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self) -> str | int | datetime | None:
        """Return the formatted metadata value."""
        probe = self.coordinator.data.get(self._probe_id)
        if probe is None:
            return None
        return self.entity_description.value_fn(probe)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the Home Assistant device for this probe."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._probe_id))},
            name=self._device_name,
            manufacturer="RIPE Atlas",
            model="Probe",
        )


def _timestamp_to_datetime(timestamp: int | None) -> datetime | None:
    """Convert RIPE Atlas Unix timestamps to Home Assistant timestamps."""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, UTC)
