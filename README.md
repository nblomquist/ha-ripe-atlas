# RIPE Atlas for Home Assistant

Unofficial third-party Home Assistant custom integration for monitoring RIPE Atlas probes via the RIPE Atlas API.

This project is not affiliated with, endorsed by, sponsored by, or maintained by Home Assistant, Nabu Casa, RIPE NCC, or the RIPE Atlas project. Home Assistant and RIPE Atlas are trademarks of their respective owners.

## Status

This project is in early development. The initial goal is to expose RIPE Atlas probe status and metadata as Home Assistant entities.

## Planned Features

- Configure a public RIPE Atlas probe by probe ID.
- Poll probe details from the RIPE Atlas REST API.
- Expose probe connection status as a Home Assistant sensor.
- Add optional API key support for `/api/v2/probes/my/` discovery.

## Development

The custom integration lives in:

```text
custom_components/ripe_atlas
```

For local testing, copy or symlink that directory into a Home Assistant `custom_components` directory and restart Home Assistant.

## License

MIT
