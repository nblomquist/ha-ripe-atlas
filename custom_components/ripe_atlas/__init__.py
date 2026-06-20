"""The RIPE Atlas integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RipeAtlasApiClient, RipeAtlasProbeNotFoundError
from .const import CONF_PROBES, DOMAIN, PLATFORMS
from .coordinator import RipeAtlasDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RIPE Atlas from a config entry."""
    session = async_get_clientsession(hass)
    client = RipeAtlasApiClient(session)
    coordinator = RipeAtlasDataUpdateCoordinator(
        hass, entry, client, entry.data[CONF_PROBES]
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady as err:
        if isinstance(err.__cause__, RipeAtlasProbeNotFoundError):
            raise ConfigEntryError(str(err.__cause__)) from err.__cause__
        raise

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a RIPE Atlas config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
