# Heliobridge Updater

[English](README.md) · [Deutsch](README.de.md)

Heliobridge Updater is a standalone Home Assistant OS app. It periodically checks the Home Assistant app store for a newer version of the Heliobridge app and can request an update through the Supervisor.

The upstream software is developed by Simon Eisenmann:
https://github.com/longsleep/heliobridge

## Installation

1. Add the repository `https://github.com/braumandl/heliobridge-haos` to the Home Assistant app store.
2. Install and configure the **Heliobridge** app.
3. Also install **Heliobridge Updater** from the same repository.
4. Start the updater and check its log.

The updater is not installed automatically with Heliobridge. The two apps are separate installations.

## Automatic update chain

The update chain consists of two independent steps:

1. GitHub Actions checks the Git tags of the upstream project `longsleep/heliobridge` every six hours.
2. The synchronization script selects the highest stable semantic version tag in the format `X.Y.Z` or `vX.Y.Z`. Prerelease versions with a suffix are ignored.
3. Before importing the source, the script checks that the version in the upstream `Cargo.toml` matches the selected tag.
4. If a new version is available, GitHub Actions updates the bundled source code and the HAOS app package version in this repository and creates a commit.
5. The updater reloads the HAOS app store and compares the installed version with the version available in the store.
6. If a newer version is available and automatic updates are enabled, the updater requests the Supervisor update. A backup is requested by default.

GitHub Actions uses the repository's `GITHUB_TOKEN` for authenticated access to the GitHub API. No personal GitHub token is required in the app configuration.

## Configuration

The options currently defined in `config.yaml` are:

| Option | Default | Description |
|---|---:|---|
| `app_name` | `Heliobridge` | Target app name |
| `app_slug` | `d166b643_heliobridge` | Full Supervisor slug of the target app in this repository |
| `check_interval_hours` | `12` | Check interval in hours |
| `backup_before_update` | `true` | Request a backup before updating |
| `auto_update` | `true` | Automatically request an available update |

If the Supervisor slug of your Heliobridge installation is different, set `app_slug` to the actual full slug. If multiple Heliobridge installations exist, explicitly select the target app by its slug.

## Network and permissions

The updater does not require a LAN IP address or a fixed installation path. It communicates through the internal Supervisor service `http://supervisor` and the `SUPERVISOR_TOKEN` variable provided by Home Assistant.

The app metadata assigns the Supervisor Manager role to the updater. This permission is required to reload the store and request an update of the target app.

## Check the log

The updater log reports, among other things:

- startup and check interval,
- detected target app and Supervisor slug,
- installed version and available store version,
- result of the update check,
- result of a requested update.

Example of a state where no update is available:

```text
[Heliobridge Updater] Updater started. Check interval: 12 hour(s).
[Heliobridge Updater] Target app: Heliobridge (d166b643_heliobridge)
[Heliobridge Updater] Installed: 0.9.1.1; Repository: 0.9.1.1
[Heliobridge Updater] Heliobridge is up to date; no update required.
```

## Test status and limitations

The updater has been started on a HAOS installation. Its log identified the target app and successfully compared the installed and available versions when they were identical.

A complete version change using a newer upstream version followed by installation through the Supervisor has not yet been demonstrated as an end-to-end test. A successful version comparison without an update does not replace this integration test.

Likewise, a successful GitHub Actions synchronization initially means only that the upstream version was checked or imported into the repository. The HAOS Supervisor must subsequently detect the new app version in the store.

## Troubleshooting

- **Target app not found:** Check the full Supervisor slug in `app_slug`.
- **No new store version:** Check the GitHub Actions workflow and then refresh the HAOS app store.
- **Update is not requested:** Check `auto_update` and the updater log.
- **Backup or Supervisor update fails:** Check the Supervisor log and available storage.
