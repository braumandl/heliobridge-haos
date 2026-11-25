# Heliobridge Home Assistant OS app

This folder contains the Home Assistant OS app package for the upstream
[Heliobridge project](https://github.com/longsleep/heliobridge).

- **App package version:** `0.9.1.1`
- **Bundled upstream source version:** `0.9.1` (see `heliobridge-source/Cargo.toml`)
- **Architecture:** `amd64`
- **App slug:** `heliobridge`

## Requirements

- Home Assistant OS with the Supervisor app store.
- An `amd64` host.
- A working Home Assistant MQTT service.
- Network connectivity from the NEXA datalogger to the Home Assistant host on TCP `7006`
  once local routing is configured.

## Install

Install this app from the public repository:

`https://github.com/braumandl/heliobridge-haos`

See the repository's top-level README for the add-repository link and step-by-step instructions.

## First start

Keep the defaults for the initial start:

```yaml
allow_writes: false
allow_power_plus: false
cloud_relay: false
```

The app obtains MQTT host, port, TLS mode and credentials from the Supervisor MQTT service.
It does not store a broker password in this repository's app options.

The app listens on TCP port `7006`. The Supervisor watchdog checks that TCP listener; this
check alone does not prove that a NEXA device is connected or that MQTT Discovery is working.

Persistent bridge state is stored in `/data/heliobridge`.

## Local network routing

The upstream project documents a DNS override for `mqtt.growatt.com` pointing to the
Home Assistant host, or destination NAT forwarding to the same host and TCP port `7006`.
This app package does not rewrite the NEXA's endpoint configuration registers.

First verify that the app starts and connects to the Home Assistant MQTT service. Only then
configure the LAN DNS override or destination-NAT rule. To return the device to its vendor
cloud path, remove the DNS override or NAT rule.

## Options

| Option | Default | Description |
|---|---:|---|
| `allow_writes` | `false` | Enables MQTT setting controls when true. |
| `allow_power_plus` | `false` | Allows the `power_plus` setting to be written when true. |
| `cloud_relay` | `false` | Enables relay traffic to the vendor cloud when true. |
| `relay_mode` | `controls` | Cloud relay policy: `full`, `controls`, or `observer`. Relevant only when cloud relay is enabled. |
| `allow_from` | empty | Comma-separated source-address/network allowlist. Empty admits all addresses. |
| `allow_devices` | empty | Comma-separated device-serial allowlist. Empty admits all serials. |
| `slots` | `1` | Number of schedule slots exposed; range 1–9. |
| `offline_after` | `30` | Seconds without telemetry before the device is reported absent. |
| `mqtt_base` | `heliobridge` | Root topic for Heliobridge MQTT topics. |
| `mqtt_discovery_prefix` | `homeassistant` | Home Assistant MQTT Discovery prefix. |
| `timezone` | `Europe/Berlin` | Time zone passed to the process. |
| `log_level` | `info` | Tracing filter passed to Heliobridge. |

The options and defaults above are taken from this app package's `config.yaml` and its
`run.sh` environment mapping. Consult upstream documentation for protocol and control details.

## Read-only behavior and control API

This app's `run.sh` does not set `HELIOBRIDGE_CONTROL_SOCKET`, so the upstream Unix control API
is not enabled by this package. With `allow_writes: false`, MQTT settings are published read-only
and MQTT commands are refused by the upstream application.

## License and upstream notices

The bundled upstream source is licensed under Apache-2.0. Its `LICENSE` and `NOTICE` files are
retained in `heliobridge-source/`. Review those files before redistributing modified source.
