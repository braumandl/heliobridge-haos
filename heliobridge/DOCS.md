# Heliobridge app documentation

See [README.md](README.md) for requirements, installation, options, first-start procedure,
network routing, and security defaults.

## Diagnostics

- Check the app log for startup errors and the MQTT service connection.
- Confirm that the app is running and that TCP port `7006` is listening.
- A successful Supervisor TCP watchdog check confirms the listener only. It does not confirm
  a NEXA connection, valid device telemetry, or MQTT Discovery entities.
- Device entities require an actual NEXA TLS/MQTT connection.
- If MQTT Discovery entities do not appear, verify the Home Assistant MQTT service and the
  configured discovery prefix.

## Returning to the vendor cloud

Stop the app and remove the LAN DNS override for `mqtt.growatt.com` or disable the
destination-NAT rule that redirects the device to the Home Assistant host. This package does
not modify the NEXA endpoint registers.
