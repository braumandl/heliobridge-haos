# Changelog

## 0.9.1.1 — Home Assistant app package

- Packages upstream Heliobridge source version `0.9.1`.
- Uses the Home Assistant Supervisor MQTT service.
- Exposes the device-facing TLS listener on TCP `7006`.
- Stores persistent bridge state under `/data/heliobridge`.
- Runs the bridge process as the dedicated unprivileged `heliobridge` user.
- Keeps MQTT writes, Power+ writes, and cloud relay disabled by default.
- Does not configure the upstream Unix control socket.

## 0.9.1 — Bundled upstream source

- Upstream source version recorded in `heliobridge-source/Cargo.toml`.
- See the upstream project changelog and README for upstream software changes:
  https://github.com/longsleep/heliobridge
