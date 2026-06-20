"""Test configuration for the RIPE Atlas integration."""

from __future__ import annotations

from pathlib import Path

import custom_components

pytest_plugins = "pytest_homeassistant_custom_component"

custom_components.__path__ = [  # type: ignore[attr-defined]
    str(Path(__file__).parents[1] / "custom_components")
]
