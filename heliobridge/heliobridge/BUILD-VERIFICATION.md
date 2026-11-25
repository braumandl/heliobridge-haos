# Build and verification status

## Inspected in the supplied package archive

- App metadata reports package version `0.9.1.1` and architecture `amd64`.
- Bundled `heliobridge-source/Cargo.toml` reports upstream source version `0.9.1`.
- `run.sh` requests the Supervisor MQTT service and maps the app options to the documented
  `HELIOBRIDGE_*` environment variables.
- `run.sh` does not set `HELIOBRIDGE_CONTROL_SOCKET`.
- The Dockerfile builds the bundled Rust source for
  `x86_64-unknown-linux-musl` and runs it on the Home Assistant `amd64` base image.
- The Dockerfile creates a dedicated user with UID/GID `65532`; the persistent state
  directory is created and assigned to that user at startup.
- The bundled upstream `LICENSE` and `NOTICE` files are present.

## Not verified by this package inspection

- A clean Docker/BuildKit build of this exact archive.
- Installation from the public GitHub repository on a clean Home Assistant OS system.
- Runtime behavior on other NEXA hardware or firmware versions.
- End-to-end DNS override or destination-NAT behavior on another user's network.
- Actual NEXA telemetry and MQTT Discovery on hardware other than the maintainer's setup.

The maintainer's existing HAOS installation has been reported as operational, but that
operational report is not a reproducible build or compatibility test for all installations.
Do not describe this package as build-verified until a clean build has been completed and
its result recorded.
