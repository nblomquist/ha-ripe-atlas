"""Config flow for RIPE Atlas."""

from __future__ import annotations

from typing import Any

import voluptuous as vol


from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_PROBE_ID, DOMAIN


class RipeAtlasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RIPE Atlas."""

    VERSION = 1


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            probe_id = user_input[CONF_PROBE_ID]
            await self.async_set_unique_id(str(probe_id))
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"RIPE Atlas Probe {probe_id}",
                data={CONF_PROBE_ID: probe_id},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_PROBE_ID): int}),
            errors=errors,
        )
