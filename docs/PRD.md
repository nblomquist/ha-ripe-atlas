# Product Requirements: RIPE Atlas for Home Assistant

## Summary
- Build an unofficial Home Assistant custom integration that monitors RIPE Atlas probes through the RIPE Atlas REST API.
- The integration creates Home Assistant entities for probe status and useful probe metadata.
- This project does not run a RIPE Atlas software probe and is not affiliated with Home Assistant, Nabu Casa, RIPE NCC, or RIPE Atlas.

## Goals
- Let a user add multiple RIPE Atlas probes by public probe ID through the Home Assistant UI.
- Let a user provide a friendly name for each configured probe during UI setup.
- Poll probe details with Home Assistant async patterns, starting with `GET https://atlas.ripe.net/api/v2/probes/{probe_id}/` per configured probe unless a supported multi-ID endpoint is verified.
- Represent each RIPE Atlas probe as its own Home Assistant device.
- Expose one probe connection status sensor per probe device.
- Add useful probe metadata without overloading changing attributes.
- Add authenticated `/api/v2/probes/my/` discovery after the UI-entered public probe path works.

## Non-Goals
- Do not build a Home Assistant add-on or container for running a RIPE Atlas software probe.
- Do not create or manage RIPE Atlas measurements in the first release.
- Do not require an API key for monitoring public probe data.
- Do not claim official support, endorsement, sponsorship, or maintenance from related projects or organizations.

## Users
- Home Assistant users who host or monitor RIPE Atlas probes.
- Users who want automations based on whether a probe is connected or disconnected.
- Users who want a lightweight view of probe metadata inside Home Assistant.

## User Stories
- As a user, I can enter multiple public probe IDs in the config flow and create one config entry.
- As a user, I can name each configured probe so Home Assistant devices are easier to recognize than probe IDs alone.
- As a user, I see each configured probe as a separate Home Assistant device.
- As a user, I see one status sensor per probe whose state maps RIPE Atlas status IDs to readable lowercase states.
- As a user, duplicate probe IDs in the same config entry are rejected or normalized away.
- As a user, a temporarily unreachable RIPE Atlas API does not break Home Assistant startup permanently.
- As a user with an API key, I can later discover probes owned by my account.

## Vertical Slices
1. UI config flow accepts and stores multiple public probe IDs plus optional friendly names in one config entry; no YAML editing is required.
2. API client fetches one public probe and maps API errors into integration exceptions.
3. Coordinator polls all configured probes using Home Assistant's shared aiohttp session.
4. Sensor platform exposes one probe status sensor per probe from coordinator data.
5. Device/entity metadata is stable and unique per probe device.
6. API-key configuration discovers owned probes from `/api/v2/probes/my/`.
7. Additional entities expose selected stable metadata only when they provide automation value.

## TDD Workflow
- Work one vertical slice at a time; do not write broad test suites ahead of implementation.
- For each slice, write one failing behavior test, implement the smallest code that passes, then repeat.
- Prefer tests through Home Assistant public integration interfaces: config flow, config entry setup, coordinator refresh, and entity state behavior.
- Mock only the external RIPE Atlas HTTP boundary; avoid mocking internal collaborators just to assert implementation details.
- Refactor only after tests for the current slice are green.
- When a slice adds setup, test, or runtime instructions, update `README.md` and `AGENTS.md` in the same change.

## RIPE Atlas API Notes
- Public probe detail endpoint: `GET /api/v2/probes/{probe_id}/`.
- Owned-probe discovery endpoint: `GET /api/v2/probes/my/` with `Authorization: Key YOUR-KEY`.
- Probe status IDs are mapped as: `0` never connected, `1` connected, `2` disconnected, `3` abandoned.
- Reading probe details does not spend RIPE Atlas measurement credits. Four probes at a 5-minute interval is about 1,152 read requests per day.
- Before optimizing polling, verify whether the probes list endpoint supports an ID filter that can fetch multiple configured probes in one request.
- Geographic data may be obfuscated by RIPE Atlas and should not be presented as exact physical location.

## Home Assistant Design Notes
- Keep the integration domain `ripe_atlas`.
- Use one integration config entry for multiple configured probes.
- Register each probe as its own Home Assistant device and attach that probe's entities to it.
- Use the probe ID for stable unique IDs and device identifiers; use the user-provided friendly name for display names when present.
- Use `DataUpdateCoordinator` for cloud polling.
- Use `CoordinatorEntity` and `SensorEntity` for sensors.
- Use the shared Home Assistant aiohttp session.
- Entity properties must return cached coordinator data only; no network I/O in properties.
- Treat RIPE Atlas API outages as update/setup failures that Home Assistant can retry or surface cleanly.

## Release Readiness
- A first usable release should support UI setup with multiple public probe IDs and friendly names, one status sensor per probe device, basic error handling, README install instructions, and a tagged GitHub release.
- HACS default inclusion is out of scope until the repo has working releases, validation workflows, documentation, and user feedback.
