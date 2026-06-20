"""Config flow for RIPE Atlas."""

from __future__ import annotations

from typing import Any

import voluptuous as vol


from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .const import CONF_PROBE_ID, CONF_PROBE_NAME, CONF_PROBES, DOMAIN


class ProbeInputError(ValueError):
    """Error raised for invalid alpha probe input."""

    def __init__(self, reason: str) -> None:
        """Initialize the probe input error."""
        super().__init__(reason)
        self.reason = reason


def _parse_probes(value: str) -> list[dict[str, int | str]]:
    """Parse alpha probe input into stored probe objects."""
    probes: list[dict[str, int | str]] = []
    seen_probe_ids: set[int] = set()

    for line in value.splitlines():
        raw_line = line.strip()
        if not raw_line:
            continue

        probe_id_text, separator, name = raw_line.partition(",")
        try:
            probe_id = int(probe_id_text.strip())
        except ValueError as err:
            raise ProbeInputError("invalid_probe") from err

        if probe_id in seen_probe_ids:
            raise ProbeInputError("duplicate_probe")
        seen_probe_ids.add(probe_id)

        probe: dict[str, int | str] = {CONF_PROBE_ID: probe_id}
        if separator and name.strip():
            probe[CONF_PROBE_NAME] = name.strip()
        probes.append(probe)

    if not probes:
        raise ProbeInputError("no_probes")

    return probes


class RipeAtlasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RIPE Atlas."""

    VERSION = 1


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                probes = _parse_probes(user_input[CONF_PROBES])
            except ProbeInputError as err:
                errors[CONF_PROBES] = err.reason
            else:
                return self.async_create_entry(
                    title="RIPE Atlas",
                    data={CONF_PROBES: probes},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROBES): TextSelector(
                        TextSelectorConfig(multiline=True)
                    )
                }
            ),
            errors=errors,
        )
