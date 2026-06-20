"""Constants for the RIPE Atlas integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "ripe_atlas"
PLATFORMS = [Platform.SENSOR]

CONF_PROBE_ID = "probe_id"
CONF_PROBES = "probes"
CONF_PROBE_NAME = "name"
