# Heliobridge for Home Assistant OS

A Home Assistant OS app packaging of [Heliobridge](https://github.com/longsleep/heliobridge),
a local TLS/MQTT bridge for the Growatt NEXA 2000.

**App package version:** `0.9.1.1`  
**Bundled upstream source version:** `0.9.1`  
**Supported architecture:** `amd64`

> This repository is an independent Home Assistant OS packaging project. It is not affiliated
> with or endorsed by Growatt or by the upstream Heliobridge author. The upstream software's
> original notices and Apache-2.0 license are retained in `heliobridge/heliobridge-source/`.

## Add this repository to Home Assistant

[![Open your Home Assistant instance and show the add app repository dialog](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/braumandl/heliobridge-haos)

Or add the repository manually:

1. Open **Settings → Apps**.
2. Open the menu in the top-right corner and select **Repositories**.
3. Add `https://github.com/braumandl/heliobridge-haos`.
4. Find **Heliobridge** in the app store and install it.

The Supervisor builds the app from the included `Dockerfile`; no prebuilt image is configured
in this repository. The build therefore depends on the build environment and availability of
the referenced base images and build dependencies.

## What this app does

- Listens for the NEXA datalogger's TLS/MQTT connection on TCP port `7006`.
- Publishes device data to the Home Assistant MQTT service.
- Uses MQTT Discovery with the configured discovery prefix.
- Stores persistent bridge state under the app's `/data` directory.
- Starts with MQTT writes, Power+ writes, and cloud relay disabled.

The app requires the Home Assistant MQTT service. A compatible MQTT app/service must be
installed and running.

## Network setup

The upstream project documents two ways to direct the NEXA datalogger to the local bridge:
a LAN DNS override for `mqtt.growatt.com` pointing to the Home Assistant host, or a
destination-NAT rule forwarding the relevant traffic to that host on TCP port `7006`.

This package does not change the NEXA endpoint registers. Do not change DNS or NAT until the
app is installed, starts successfully, and its MQTT connection to Home Assistant is healthy.
The device's network path must permit it to reach the Home Assistant host on TCP `7006`.

## Security defaults

The app defaults to:

```yaml
allow_writes: false
allow_power_plus: false
cloud_relay: false
```

The two connection allowlists (`allow_from` and `allow_devices`) are empty by default. In the
bundled upstream software, an empty allowlist admits all connecting addresses or device serials.
Configure them if you need to restrict access; do not interpret an empty value as deny-all.

## Documentation

- [App installation, configuration and network setup](heliobridge/README.md)
- [App documentation](heliobridge/DOCS.md)
- [Changelog](heliobridge/CHANGELOG.md)
- [Build verification scope](heliobridge/BUILD-VERIFICATION.md)

## Versioning

The Home Assistant app package and the bundled upstream application use separate version
numbers. Update both deliberately when preparing a new release:
- App package: `heliobridge/config.yaml`
- Upstream source: `heliobridge/heliobridge-source/Cargo.toml`

## Support and attribution

For upstream Heliobridge software issues, consult the
[upstream project](https://github.com/longsleep/heliobridge). For packaging-specific issues,
use the Issues tab of this repository.

Growatt and NEXA are trademarks of their respective owners. This project is an independent
integration and is not an official Growatt product.
