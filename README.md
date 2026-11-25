# Heliobridge for Home Assistant OS

[English](README.md) · [Deutsch](README.de.md)

This repository provides two independent Home Assistant OS apps for operating the Growatt NEXA 2000 with Home Assistant:

1. **Heliobridge** – packages the original software by Simon Eisenmann as a HAOS app. It accepts the TLS connection from the NEXA data logger and publishes data through the Home Assistant MQTT service and MQTT Discovery.
2. **Heliobridge Updater** – periodically checks the app store and can install a newer Heliobridge app version through the Home Assistant Supervisor.

The Heliobridge software itself is developed by Simon Eisenmann:
https://github.com/longsleep/heliobridge

This repository contains the HAOS packaging and the associated update infrastructure. It is an independent community project, not an official Growatt product and not an official part of the upstream project.

---

## Contents

- [Requirements](#requirements)
- [Add the repository to Home Assistant](#add-the-repository-to-home-assistant)
- [App 1: Install Heliobridge](#app-1-install-heliobridge)
- [Configure Heliobridge](#configure-heliobridge)
- [Set up network redirection](#set-up-network-redirection)
- [App 2: Install Heliobridge Updater](#app-2-install-heliobridge-updater)
- [How the automatic update chain works](#how-the-automatic-update-chain-works)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)
- [Versions and technical details](#versions-and-technical-details)
- [Upstream project and notices](#upstream-project-and-notices)

## Requirements

- Home Assistant OS with Supervisor.
- Home Assistant MQTT service, for example Mosquitto, installed and running.
- Growatt NEXA 2000 with network connectivity.
- A network path from the NEXA data logger to the Home Assistant host on TCP port `7006`.
- The app metadata currently lists only the `amd64` architecture.

## Add the repository to Home Assistant

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/braumandl/heliobridge-haos)

Alternatively, add it manually:

1. Open Home Assistant and go to **Settings → Apps**.
2. Open the menu in the top-right corner of the app store.
3. Select **Repositories**.
4. Add this URL:

   `https://github.com/braumandl/heliobridge-haos`

5. Refresh the app store.

Adding the repository does not install the apps. **Heliobridge and Heliobridge Updater must be installed separately.**

## App 1: Install Heliobridge

1. Select **Heliobridge** from this repository in the app store.
2. Install it.
3. Review the configuration before starting the app.
4. Start the app.
5. Check the app log.

The app uses the Home Assistant MQTT service. The log should show a successful connection to the MQTT service. The TLS listener for the NEXA data logger uses TCP port `7006`.

A running TCP listener alone does not prove that the NEXA data logger has connected. Devices and MQTT Discovery entities appear only after the data logger establishes a connection and sends data.

## Configure Heliobridge

The app options are managed through the Home Assistant configuration UI. The options currently defined in `heliobridge/config.yaml` are:

| Option | Default | Description |
|---|---:|---|
| `allow_writes` | `false` | Allows write/control commands |
| `allow_power_plus` | `false` | Enables Power+ write functions |
| `cloud_relay` | `false` | Enables forwarding to the Growatt cloud |
| `relay_mode` | `controls` | Relay mode: `full`, `controls`, or `observer` |
| `allow_from` | empty | Optional list of allowed source IP addresses/networks |
| `allow_devices` | empty | Optional list of allowed device serial numbers |
| `slots` | `1` | Number of schedule slots (1–9) |
| `offline_after` | `30` | Seconds without telemetry before a device is considered offline |
| `mqtt_base` | `heliobridge` | MQTT base topic |
| `mqtt_discovery_prefix` | `homeassistant` | MQTT Discovery prefix |
| `timezone` | `Europe/Berlin` | Time zone |
| `log_level` | `info` | Logging level |

### Security notes on the defaults

For the initial setup, write functions and the cloud relay remain disabled:

```yaml
allow_writes: false
allow_power_plus: false
cloud_relay: false
```

The `allow_from` and `allow_devices` options are empty by default. **In the bundled upstream code, an empty allowlist does not mean “nobody is allowed”; no restriction based on that list is applied.** To restrict access, configure these lists explicitly.

Enable write functions and the cloud relay only after understanding their effects and checking the intended operating mode.

## Set up network redirection

The NEXA data logger must be able to reach the local Heliobridge listener. The upstream project documents two approaches:

- **DNS override:** Resolve `mqtt.growatt.com` to the IP address of the Home Assistant host on the local network.
- **Destination NAT:** Forward the relevant traffic to the Home Assistant host on TCP port `7006`.

The exact setup depends on the router and network topology. This HAOS app does not configure the DNS override or NAT rule itself. It also does not modify any NEXA endpoint registers.

**Recommended order:** First install and start Heliobridge. Then check that MQTT is connected and TCP port `7006` is listening. Only after that, configure the network redirection. Once redirected, check the incoming connection from the NEXA data logger and the MQTT devices in Home Assistant.

To return to the normal cloud path, remove the DNS redirection or destination NAT rule that you configured.

## App 2: Install Heliobridge Updater

The updater is a **separate, optional app**. Adding the repository or installing Heliobridge does not install the updater automatically.

1. Select **Heliobridge Updater** from the same app repository.
2. Install it separately.
3. Start it.
4. Check the updater log.

The updater requires Supervisor Manager permissions to reload the app store and request an app update.

### Updater options

The options currently defined in `heliobridge-updater/config.yaml` are:

| Option | Default | Description |
|---|---:|---|
| `app_name` | `Heliobridge` | Target app name |
| `app_slug` | `d166b643_heliobridge` | Full Supervisor slug of the target app |
| `check_interval_hours` | `12` | Check interval in hours |
| `backup_before_update` | `true` | Request a backup before updating |
| `auto_update` | `true` | Automatically request available updates |

The configured default slug, `d166b643_heliobridge`, matches the Heliobridge app from this repository. If the repository slug or target installation differs, check and adjust this value.

The updater communicates internally through `http://supervisor` and the `SUPERVISOR_TOKEN` variable provided by Home Assistant. No fixed LAN IP address or installation path is configured.

## How the automatic update chain works

The update chain consists of two separate steps:

### 1. Sync the upstream source into this repository

The GitHub Actions workflow **Sync upstream Heliobridge release** runs every six hours on a schedule and can also be started manually.

The script `scripts/sync-upstream.py`:

- queries the Git tags of the upstream project through the GitHub Tags API,
- selects the highest stable tag in the format `X.Y.Z` or `vX.Y.Z`,
- excludes tags with a prerelease suffix,
- downloads the archive for the selected tag,
- checks that the version in `Cargo.toml` matches the tag,
- imports the source code and updates the HAOS package version.

The HAOS package version currently follows the scheme `<upstream-version>.1`. If files change, the workflow creates a commit in this repository.

### 2. Install the new app version in Home Assistant

The Heliobridge Updater reloads the Home Assistant app store, compares the installed and available app versions, and—if a newer version is available and `auto_update` is enabled—requests the Supervisor update. By default, it also requests a backup.

The GitHub synchronization workflow and the HAOS updater are independent. The new version must first be imported successfully into this repository; only then can the Supervisor detect it in the store.

### Current test status

The GitHub Actions synchronization was run against the existing upstream tag `v0.9.1`. The workflow detected that this version had already been mirrored, so no commit was required.

The updater was started on a HAOS installation. Its log confirmed the target app `d166b643_heliobridge`, compared version `0.9.1.1` with `0.9.1.1`, and reported that no update was required.

**A complete version change using a newer upstream version followed by a Supervisor update has therefore not yet been demonstrated.** The automatic update chain should be considered implemented, but not yet fully integration-tested through an actual version change.

## Troubleshooting

### Heliobridge does not connect to MQTT

- Check that the Home Assistant MQTT service is installed and running.
- Check the Heliobridge log for the MQTT connection.
- Check MQTT credentials or the Supervisor MQTT service.

### No connection from the NEXA data logger

- Check the DNS resolution of `mqtt.growatt.com` or the destination NAT rule.
- Check reachability of the Home Assistant host on TCP port `7006`.
- Check the Heliobridge log for incoming TLS connections.

### No MQTT Discovery entities

- Check that the NEXA data logger is actually connected and sending telemetry.
- Check the MQTT service and Discovery prefix.
- Check the Heliobridge log for successful MQTT publication.

### Updater reports no new version

- Open GitHub Actions and inspect the **Sync upstream Heliobridge release** run.
- Make sure the workflow completed successfully.
- Check whether the updated app version appears in the Home Assistant app store.
- Check the updater log for the target slug and version comparison.

### Updater cannot find the target app

Set `app_slug` to the full Supervisor slug of the intended Heliobridge installation. If multiple Heliobridge apps are installed, do not rely on automatic name matching.

## Uninstallation

The apps can be removed independently.

- **Uninstall only the updater:** Heliobridge continues to run; app updates must then be installed manually through the app store.
- **Uninstall Heliobridge:** First remove the DNS or destination NAT redirection, or restore the data logger's intended network path. Then uninstall the app.

A current Home Assistant backup is recommended before uninstalling or making major changes.

## Versions and technical details

Currently in this repository:

- HAOS app package version: `0.9.1.1`
- Bundled upstream source version: `0.9.1`
- Heliobridge app architecture: `amd64`
- TLS listener: TCP `7006`
- Persistent Heliobridge state: `/data/heliobridge`

The Heliobridge binary is built in the Dockerfile from the bundled Rust source code. No pre-built image is specified in the app configuration; the Supervisor therefore builds the app from the Dockerfile during installation.

Further technical information:

- [Heliobridge app documentation](heliobridge/DOCS.md)
- [Heliobridge changelog](heliobridge/CHANGELOG.md)
- [Build and verification status](heliobridge/BUILD-VERIFICATION.md)
- [Updater documentation](heliobridge-updater/DOCS.md)
- [Updater README](heliobridge-updater/README.md)

## Project status and contributions

**This repository is currently not actively developed or maintained on an ongoing basis.** It is provided in its current form; regular maintenance, prompt bug fixes, or further development cannot be guaranteed.

The project is explicitly open to contributors and to a handover of maintenance. Anyone interested in maintaining the apps, upstream synchronization, or documentation is welcome. Possible contributions include:

- investigating and fixing bugs,
- testing compatibility with newer Home Assistant OS and Supervisor versions,
- maintaining the automatic upstream synchronization and updater,
- extending and updating the documentation,
- sharing responsibility for releases and support.

Interested contributors can get in touch through **GitHub Issues** or **Pull Requests**. Anyone willing to take a more active role and share long-term maintenance can explicitly mention this in an issue. Collaboration or a handover is welcome.

Please note: Without active maintainers, issues and pull requests may remain unanswered.

## Upstream project and license notices

The Heliobridge software itself is by Simon Eisenmann:

https://github.com/longsleep/heliobridge

The upstream copyright notices and the license and NOTICE files are retained in the bundled source code. Please observe the original project's license terms when redistributing or modifying the software.

This repository is independent of Growatt. Growatt and NEXA are trademarks of their respective owners.
