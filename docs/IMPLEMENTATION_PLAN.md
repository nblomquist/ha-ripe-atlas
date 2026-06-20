# 0.0.1 Alpha Implementation Plan

## Target Outcome
- A user installs the custom integration and configures multiple public RIPE Atlas probes from the Home Assistant UI.
- Each configured probe has a RIPE Atlas probe ID and an optional friendly name.
- One Home Assistant config entry owns all configured probes.
- Each probe is registered as a separate Home Assistant device.
- Each probe device exposes one status sensor with lowercase states: `never_connected`, `connected`, `disconnected`, or `abandoned`.
- Local tests can be run from this repository.

## Working Rules
- Use vertical slices. Do not build all test infrastructure, all API code, all coordinator code, and all entities as separate horizontal phases.
- For each slice: write one failing behavior test, run it red, implement the minimum code to pass, run it green, then refactor only if needed.
- Prefer Home Assistant public interfaces in tests: config flow, config entry setup, coordinator refresh, entity registry/device registry, and entity state.
- Mock only the RIPE Atlas HTTP boundary unless there is a concrete reason to mock something else.
- When a slice changes setup, test commands, runtime behavior, or workflow, update `README.md` and `AGENTS.md` in the same change.

## Slice 1: Local Test Harness

### Behavior
Developers can install test dependencies and run the local test suite with one documented command.

### RED
- Add a minimal test such as `tests/test_scaffold.py` that imports the integration domain or checks the manifest can be loaded.
- Run the documented test command before dependencies/config are complete and confirm it fails for missing test setup or missing command support.

### GREEN
- Add `pyproject.toml` with project metadata and test dependencies.
- Add pytest configuration for Home Assistant custom component tests.
- Add any required `tests/conftest.py` for `pytest-homeassistant-custom-component`.
- Document exact setup and test commands in `README.md`.
- Add the same commands to `AGENTS.md` under verification.

### Verify
- `mise install`
- `mise exec -- python -m venv .venv`
- `source .venv/bin/activate`
- `python -m pip install -e ".[test]"`
- `pytest`

## Slice 2: UI Config Flow Stores Multiple Probes

### Behavior
A user can create one config entry from the Home Assistant UI containing multiple probe IDs and optional friendly names.

### RED
- Write one config-flow behavior test that submits two probes, for example `12345:Home Fiber` and `67890:Office Probe`, and expects one created config entry.
- Assert stored data preserves stable probe IDs and friendly names.
- Assert no YAML configuration is required.

### GREEN
- Replace the single `probe_id` form with a UI field that accepts multiple probes in a simple alpha format.
- Recommended alpha input format: one probe per line, `probe_id[,friendly name]`.
- Normalize probe IDs to integers and trim friendly names.
- Store data as a list of probe objects, not as display strings.

### Verify
- Run the focused config-flow test.
- Run the full test suite.

## Slice 3: Duplicate And Invalid UI Input Handling

### Behavior
The config flow handles bad input predictably before creating an entry.

### RED
- Write one config-flow test for duplicate probe IDs in the same submission.
- Expected behavior: reject duplicates with a form error, or normalize duplicates away. Pick one behavior and test only that behavior.

### GREEN
- Implement the smallest parser/validation path for the chosen duplicate behavior.
- Reject blank input and non-integer probe IDs with user-visible form errors.
- Do not call RIPE Atlas from the config flow in 0.0.1.

### Verify
- Run the focused config-flow validation test.
- Run the full test suite.

## Slice 4: RIPE Atlas API Client Fetches One Probe

### Behavior
The API client fetches a single public probe by ID and returns normalized probe data needed by the status sensor.

### RED
- Write one async API-client test with a mocked HTTP response from `GET /api/v2/probes/{probe_id}/`.
- Assert the returned object includes probe ID and status ID.

### GREEN
- Implement an async API client using an injected aiohttp-compatible session.
- Add minimal integration exceptions for not found and communication/API errors.
- Keep the client independent of Home Assistant entity classes.

### Verify
- Run the focused API-client test.
- Run the full test suite.

## Slice 5: API Error Mapping

### Behavior
The API client maps RIPE Atlas failures into predictable integration exceptions.

### RED
- Write one API-client test for a `404` probe response.
- Assert it raises a probe-not-found exception that setup can treat as a permanent config problem.

### GREEN
- Implement `404` handling.
- Map timeout/client errors to communication errors.
- Map malformed payloads to API errors.

### Verify
- Run the focused API-client error test.
- Run the full test suite.

## Slice 6: Coordinator Polls All Configured Probes

### Behavior
The coordinator polls every configured probe and stores data keyed by probe ID.

### RED
- Write one coordinator/setup behavior test with two configured probes and mocked RIPE Atlas responses.
- Assert first refresh results in coordinator data for both probe IDs.

### GREEN
- Implement `RipeAtlasDataUpdateCoordinator` as a real `DataUpdateCoordinator`.
- Use Home Assistant's shared aiohttp session from setup.
- Poll each configured probe with `GET /api/v2/probes/{probe_id}/`.
- Use a 5-minute update interval for alpha.
- Defer multi-ID endpoint optimization until verified against RIPE Atlas docs or live behavior.

### Verify
- Run the focused coordinator/setup test.
- Run the full test suite.

## Slice 7: Status Sensor Per Probe Device

### Behavior
Each configured probe creates one status sensor attached to that probe's Home Assistant device.

### RED
- Write one Home Assistant setup/entity behavior test with two configured probes.
- Assert two status entities are created.
- Assert each entity state maps the RIPE status ID to the expected lowercase state.
- Assert each entity has a stable unique ID based on probe ID.
- Assert each entity is associated with the correct probe device.

### GREEN
- Implement `CoordinatorEntity` + `SensorEntity` status entities.
- Use stable unique IDs like `<probe_id>_status`.
- Use device identifiers based on `(DOMAIN, str(probe_id))`.
- Use friendly names for device display names when present; otherwise fall back to `RIPE Atlas Probe <probe_id>`.
- Do not add metadata sensors or changing attributes in 0.0.1.

### Verify
- Run the focused entity/device test.
- Run the full test suite.

## Slice 8: Bad Probe Runtime Behavior

### Behavior
A bad probe ID fails cleanly at setup and can be fixed by deleting the config entry and creating a new one.

### RED
- Write one setup behavior test where RIPE Atlas returns `404` for a configured probe.
- Assert Home Assistant setup surfaces a non-retryable config problem or fails cleanly without creating misleading entities.

### GREEN
- Convert the API client's not-found exception into the appropriate Home Assistant setup failure.
- Keep README clear that 0.0.1 alpha fixes bad probe IDs by deleting and recreating the config entry; reconfigure flow is later.

### Verify
- Run the focused bad-probe setup test.
- Run the full test suite.

## Slice 9: Runtime Install Documentation

### Behavior
A tester can run local tests and manually install the integration into a Home Assistant instance.

### RED
- Treat missing or stale instructions as the failing behavior: README lacks exact commands needed by a new tester.

### GREEN
- Update `README.md` with exact local test commands.
- Update `README.md` with copy/symlink installation instructions.
- Update `AGENTS.md` with the verified command list and known limitations.

### Verify
- Run documented local test command.
- If a Home Assistant instance is available, copy/symlink `custom_components/ripe_atlas`, restart Home Assistant, and verify the integration appears in the UI.

## Slice 10: Alpha Release Prep

### Behavior
The repository is ready for a tagged `0.0.1-alpha` release.

### RED
- Check release readiness against `docs/PRD.md`; any missing alpha requirement is a failing item.

### GREEN
- Update version in `manifest.json` if needed.
- Add a short changelog or release notes section.
- Confirm README states alpha limitations: public probes only, UI-entered probe IDs, no API key discovery, no YAML setup, no reconfigure flow.
- Push and tag only after tests are green and docs match behavior.

### Verify
- Run the full test suite.
- Inspect `git status`, `git diff`, and release notes before tagging.
