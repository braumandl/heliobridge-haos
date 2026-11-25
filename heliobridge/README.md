# Heliobridge – Home Assistant OS App

[English](README.md) · [Deutsch](README.de.md)

This app packages the original [Heliobridge software by Simon Eisenmann](https://github.com/longsleep/heliobridge) for Home Assistant OS.

It provides a local TLS/MQTT bridge for the Growatt NEXA 2000 and publishes device data through the Home Assistant MQTT service and MQTT Discovery.

## Requirements

- Home Assistant OS with Supervisor on the `amd64` architecture listed in `config.yaml`.
- Installed and running Home Assistant MQTT service.
- Network connectivity from the NEXA data logger to the Home Assistant host on TCP port `7006`.

## Installation

1. Add the repository `https://github.com/braumandl/heliobridge-haos` to the Home Assistant app store.
2. Select and install the **Heliobridge** app.
3. Review the configuration and start the app.
4. Check the app log for the MQTT connection and the TLS listener startup.

The Heliobridge Updater app is a separate optional app and must be installed separately if required.

## Options

| Option | Default | Description |
|---|---:|---|
| `allow_writes` | `false` | Allow write/control commands |
| `allow_power_plus` | `false` | Enable Power+ write functions |
| `cloud_relay` | `false` | Enable Growatt cloud relay |
| `relay_mode` | `controls` | Relay mode: `full`, `controls`, or `observer` |
| `allow_from` | empty | Optional source IP/network allowlist |
| `allow_devices` | empty | Optional device serial number allowlist |
| `slots` | `1` | Number of schedule slots (1–9) |
| `offline_after` | `30` | Seconds without telemetry before offline |
| `mqtt_base` | `heliobridge` | MQTT base topic |
| `mqtt_discovery_prefix` | `homeassistant` | MQTT Discovery prefix |
| `timezone` | `Europe/Berlin` | Time zone |
| `log_level` | `info` | Logging level |

### Security defaults

Write functions and the cloud relay are disabled by default:

```yaml
allow_writes: false
allow_power_plus: false
cloud_relay: false
```

In the bundled upstream code, empty values for `allow_from` and `allow_devices` mean that no restriction is applied based on these lists. Empty lists are therefore not a deny-all rule.

## Network redirection

The NEXA data logger must be redirected to the local bridge. The upstream project documents:

- a DNS override for `mqtt.growatt.com` to the IP address of the Home Assistant host, or
- destination NAT to the Home Assistant host on TCP port `7006`.

The app does not configure these network rules itself and does not modify NEXA endpoint registers. Configure DNS/NAT only after the app starts and its MQTT connection has been established successfully.

## Troubleshooting

- Check the MQTT connection in the app log.
- Check that TCP port `7006` is listening.
- Check whether the NEXA data logger actually establishes a TLS connection.
- Check MQTT Discovery and the configured Discovery prefix.

A successful TCP watchdog test confirms only that the listener is reachable. It does not prove that a NEXA device is connected or that valid telemetry and MQTT Discovery data are being published.

## Return to the Growatt cloud

Stop the app and remove the configured DNS override for `mqtt.growatt.com` or the destination NAT rule. This package does not modify NEXA endpoint registers.
