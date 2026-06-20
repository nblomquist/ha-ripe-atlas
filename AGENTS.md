# Agent Notes

## Project Scope
- This is an unofficial third-party Home Assistant custom integration. Do not imply sponsorship, endorsement, or maintenance by Home Assistant, Nabu Casa, RIPE NCC, or RIPE Atlas.
- The integration reads RIPE Atlas API data into Home Assistant entities; it is not a Home Assistant add-on for running a RIPE Atlas software probe.

## Layout
- Integration code lives under `custom_components/ripe_atlas/`; keep the Home Assistant domain as `ripe_atlas`.
- `manifest.json` declares a HACS/custom integration with `config_flow: true`, `integration_type: service`, `iot_class: cloud_polling`, and version `0.0.2-alpha`.
- `__init__.py` creates a RIPE Atlas API client with Home Assistant's shared aiohttp session, creates the coordinator, performs first refresh, stores the coordinator in `hass.data[DOMAIN][entry.entry_id]["coordinator"]`, and forwards platforms listed in `const.py`; currently only `Platform.SENSOR`.
- `config_flow.py` accepts multiple UI-entered public probe IDs with optional friendly names in one config entry. Alpha input format is one probe per line: `probe_id` or `probe_id, friendly name`.
- `config_flow.py` also implements a reconfigure flow to edit the existing probe list. It uses the same multiline alpha input format and updates/reloads the config entry.
- The config flow and reconfigure flow reject blank input, duplicate probe IDs, and non-integer probe IDs before creating/updating an entry. They do not call RIPE Atlas.
- `api.py` fetches public probe details from `GET https://atlas.ripe.net/api/v2/probes/{probe_id}/` with an injected aiohttp-compatible session and maps RIPE Atlas failures to integration exceptions.
- `coordinator.py` implements `RipeAtlasDataUpdateCoordinator` with a 5-minute update interval and stores normalized probe data keyed by probe ID.
- `sensor.py` creates one status `SensorEntity` per configured probe, attached to a per-probe device with identifiers `(DOMAIN, str(probe_id))` and unique IDs like `<probe_id>_status`.

## Verification
- Python is pinned with `mise.toml` to `3.14.5`, matching Home Assistant core's current development `.python-version`; use `mise install` before creating a venv when using mise.
- Local test setup: `mise install`, `mise exec -- python -m venv .venv`, `source .venv/bin/activate`, `python -m pip install -e ".[test]"`.
- Run local tests with `pytest` after activating `.venv`.
- Current verified test suite covers the config flow, reconfigure flow, API client, coordinator setup, status entities/devices, bad probe setup behavior, and scaffold manifest expectations.
- No lint, typecheck, CI, lockfile, or formatter config exists yet. Do not invent those commands; verify with tests and targeted syntax/import checks until tooling is added.
- For Home Assistant runtime testing, use the README workflow: copy or symlink `custom_components/ripe_atlas` into a Home Assistant `custom_components` directory and restart Home Assistant.
- If a configured probe returns 404 during setup, Home Assistant marks the entry as a non-retryable setup error and no entities are created. In `0.0.2-alpha`, users can fix probe IDs through the reconfigure flow when Home Assistant exposes the entry configuration action; otherwise they can delete and recreate the config entry.

## Product Plan
- Use `docs/PRD.md` as the current product source of truth.
- Use `docs/IMPLEMENTATION_PLAN.md` for the step-by-step 0.0.1 alpha build sequence.
- Work in vertical slices. Do not build broad horizontal layers beyond the slice being tested.
- Use TDD for feature work: one failing behavior test, minimal implementation, then refactor only after green.
- Keep tests focused on public Home Assistant behavior and mock only the RIPE Atlas HTTP boundary where practical.
- When a change adds or changes setup, verification, or workflow instructions, update both `README.md` and this file in the same change.

## Implementation Preferences
- Prefer Home Assistant async patterns: shared aiohttp session, `DataUpdateCoordinator`, `CoordinatorEntity`, and `SensorEntity`.
- Network I/O belongs in the API client/coordinator, not entity properties.
- Model one integration config entry with multiple probe devices; attach each probe's entities to its probe device.
- Use probe IDs for stable unique IDs/device identifiers; use user-provided friendly names for display names when available.
- Start with public probe lookup by `GET https://atlas.ripe.net/api/v2/probes/{probe_id}/` for each configured probe; only optimize to a multi-ID list endpoint after verifying RIPE Atlas supports it.
- Add API key support only when implementing authenticated discovery.
- Do not add metadata sensors, changing attributes, YAML setup, or API-key discovery to the current alpha unless the product plan changes.
- Home Assistant config flows do not provide an inline dynamic `+` row UI for arbitrary repeated objects. If improving the probe-entry UX, prefer a native repeated-step flow: enter one probe ID/name, then choose add another or finish.
