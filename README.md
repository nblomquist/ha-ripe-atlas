# RIPE Atlas for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/nblomquist/ha-ripe-atlas?style=for-the-badge)](https://github.com/nblomquist/ha-ripe-atlas/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/docs/faq/custom_repositories/)
[![License](https://img.shields.io/github/license/nblomquist/ha-ripe-atlas?style=for-the-badge)](LICENSE)

Unofficial third-party Home Assistant custom integration for monitoring RIPE Atlas probes via the RIPE Atlas API.

This project is not affiliated with, endorsed by, sponsored by, or maintained by Home Assistant, Nabu Casa, RIPE NCC, or the RIPE Atlas project. Home Assistant and RIPE Atlas are trademarks of their respective owners.

## Status

This project is in early alpha development. Version `0.0.1-alpha` exposes public RIPE Atlas probe status as Home Assistant sensor entities, with each configured probe represented as its own Home Assistant device.

Product direction is tracked in [`docs/PRD.md`](docs/PRD.md). The 0.0.1 alpha build sequence is tracked in [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md). Development should proceed in small vertical slices using test-driven development.

## Alpha Features

- Configure multiple public RIPE Atlas probes by probe ID from the Home Assistant UI in one integration config entry.
- Give each configured probe an optional friendly device name.
- Poll `GET https://atlas.ripe.net/api/v2/probes/{probe_id}/` for each configured probe every 5 minutes.
- Represent each RIPE Atlas probe as a Home Assistant device.
- Expose one status sensor per probe device.
- Map RIPE Atlas status IDs to lowercase states: `never_connected`, `connected`, `disconnected`, or `abandoned`.

## Alpha Limitations

- Public probes only.
- Probe IDs are entered manually in the UI; there is no YAML setup.
- API key discovery through `/api/v2/probes/my/` is not implemented yet.
- Reconfigure/edit flow is not implemented yet. To fix a bad probe ID in `0.0.1-alpha`, delete the config entry and create it again.
- No metadata sensors are included in `0.0.1-alpha`; only the status sensor is created per probe.

## Installation

### Option A: HACS Custom Repository

This integration is not in the HACS default repository list yet. Install it as a HACS custom repository.

[![Open your Home Assistant instance and add this repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nblomquist&repository=ha-ripe-atlas&category=integration)

Manual HACS steps:

1. Open **HACS > Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/nblomquist/ha-ripe-atlas`.
4. Select category **Integration**.
5. Install **RIPE Atlas**.
6. Restart Home Assistant.

### Option B: Manual Install

Copy the integration directory into your Home Assistant configuration directory:

```sh
mkdir -p /path/to/homeassistant/config/custom_components
cp -R custom_components/ripe_atlas /path/to/homeassistant/config/custom_components/
```

For development, a symlink avoids repeated copies:

```sh
mkdir -p /path/to/homeassistant/config/custom_components
ln -s /path/to/ha-ripe-atlas/custom_components/ripe_atlas /path/to/homeassistant/config/custom_components/ripe_atlas
```

Restart Home Assistant after copying or symlinking the integration.

## Configuration

Add the integration from the Home Assistant UI. Enter one public RIPE Atlas probe per line using this alpha format:

```text
12345, Home Fiber
67890, Office Probe
```

The friendly name after the comma is optional:

```text
12345
67890, Office Probe
```

Duplicate probe IDs, blank input, and non-integer probe IDs are rejected before the config entry is created. The config flow does not call RIPE Atlas.

During setup, the integration fetches each configured probe from RIPE Atlas. A missing probe returns a permanent setup error and creates no misleading entities. Temporary communication failures are left retryable by Home Assistant.

## Development

Home Assistant core currently requires Python 3.14.2 or newer; this repo pins Python 3.14.5 in `mise.toml` to match Home Assistant core's current development version.

Set up the local Python environment:

```sh
mise install
mise exec -- python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
pytest
```

The custom integration source lives in:

```text
custom_components/ripe_atlas
```

### Development Workflow

- Build one vertical slice at a time.
- Use TDD for implementation work: one failing behavior test, minimal implementation, then refactor after green.
- When setup, verification, or usage instructions change, update this README and `AGENTS.md` in the same change.
- Run local tests with `pytest` after activating `.venv`.
- No project lint/typecheck commands exist yet; add and document them before relying on them.

## Release Notes

### 0.0.1-alpha

- Initial alpha custom integration scaffold.
- UI config flow for multiple manually entered public probe IDs with optional friendly names.
- RIPE Atlas API client, coordinator polling, and one status sensor per probe device.
- Basic config-flow validation and bad-probe setup handling.
- Local pytest-based Home Assistant custom-component test harness.

## License

MIT
