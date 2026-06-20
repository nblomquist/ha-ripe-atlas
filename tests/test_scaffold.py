"""Scaffold tests for the RIPE Atlas integration."""

from __future__ import annotations

import json
from pathlib import Path


def test_manifest_declares_expected_domain() -> None:
    """Test the custom integration manifest declares the expected domain."""
    manifest_path = (
        Path(__file__).parents[1]
        / "custom_components"
        / "ripe_atlas"
        / "manifest.json"
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["domain"] == "ripe_atlas"
    assert manifest["config_flow"] is True
    assert manifest["integration_type"] == "service"
    assert manifest["iot_class"] == "cloud_polling"
    assert manifest["version"] == "0.0.1-alpha"
