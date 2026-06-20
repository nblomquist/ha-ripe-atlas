"""Config flow tests for the RIPE Atlas integration."""

from __future__ import annotations

import pytest

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ripe_atlas.const import CONF_PROBES, DOMAIN


pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


async def test_user_flow_stores_multiple_probes(
    hass: HomeAssistant,
) -> None:
    """Test the user flow stores multiple probes with friendly names."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_PROBES: "12345, Home Fiber\n67890, Office Probe"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "RIPE Atlas"
    assert result["data"] == {
        CONF_PROBES: [
            {"probe_id": 12345, "name": "Home Fiber"},
            {"probe_id": 67890, "name": "Office Probe"},
        ]
    }


@pytest.mark.parametrize(
    ("probes", "error"),
    [
        ("12345, Home\n12345, Duplicate", "duplicate_probe"),
        ("\n  \n", "no_probes"),
        ("not-a-probe, Home", "invalid_probe"),
    ],
)
async def test_user_flow_rejects_invalid_probe_input(
    hass: HomeAssistant,
    probes: str,
    error: str,
) -> None:
    """Test the user flow rejects invalid probe input before entry creation."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_PROBES: probes}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_PROBES: error}
