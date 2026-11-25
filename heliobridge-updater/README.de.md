# Heliobridge Updater

[English](README.md) · [Deutsch](README.de.md)

Der Heliobridge Updater ist eine eigenständige Home-Assistant-OS-App. Er prüft den Home-Assistant-App-Store regelmäßig auf eine neuere Version der Heliobridge-App und kann ein Update über den Supervisor anfordern.

Die Upstream-Software wird von Simon Eisenmann entwickelt:
https://github.com/longsleep/heliobridge

## Installation

1. Zuerst das Repository `https://github.com/braumandl/heliobridge-haos` zum Home-Assistant-App-Store hinzufügen.
2. Die App **Heliobridge** installieren und einrichten.
3. Zusätzlich die App **Heliobridge Updater** aus demselben Repository installieren.
4. Den Updater starten und sein Protokoll kontrollieren.

Der Updater wird nicht automatisch mit der Heliobridge installiert. Beide Apps sind getrennte Installationen.

## Automatische Updatekette

Die Updatekette besteht aus zwei unabhängigen Schritten:

1. GitHub Actions prüft alle sechs Stunden die Git-Tags des Originalprojekts `longsleep/heliobridge`.
2. Das Synchronisierungsskript wählt den höchsten stabilen semantischen Versions-Tag im Format `X.Y.Z` bzw. `vX.Y.Z`. Vorabversionen mit Suffix werden nicht berücksichtigt.
3. Vor der Übernahme wird geprüft, ob die Versionsnummer in der Upstream-`Cargo.toml` mit dem ausgewählten Tag übereinstimmt.
4. Bei einer neuen Version aktualisiert GitHub Actions den gebündelten Quellcode und die HAOS-App-Paketversion in diesem Repository und erstellt einen Commit.
5. Der Updater lädt den HAOS-App-Store neu und vergleicht die installierte Version mit der im Store verfügbaren Version.
6. Wenn eine neuere Version verfügbar ist und automatische Updates aktiviert sind, fordert der Updater das Supervisor-Update an. Standardmäßig wird dabei ein Backup angefordert.

GitHub Actions verwendet den Repository-`GITHUB_TOKEN` für den authentifizierten Zugriff auf die GitHub-API. Es ist kein persönlicher GitHub-Token in der App-Konfiguration erforderlich.

## Konfiguration

Die aktuell in `config.yaml` definierten Optionen:

| Option | Standardwert | Bedeutung |
|---|---:|---|
| `app_name` | `Heliobridge` | Name der Ziel-App |
| `app_slug` | `d166b643_heliobridge` | Vollständiger Supervisor-Slug der Ziel-App aus diesem Repository |
| `check_interval_hours` | `12` | Prüfintervall in Stunden |
| `backup_before_update` | `true` | Vor dem Update ein Backup anfordern |
| `auto_update` | `true` | Ein verfügbares Update automatisch anfordern |

Wenn der Supervisor-Slug deiner Heliobridge-Installation abweicht, muss `app_slug` auf den tatsächlichen vollständigen Slug angepasst werden. Bei mehreren Heliobridge-Installationen sollte die Ziel-App ausdrücklich über ihren Slug festgelegt werden.

## Netzwerk- und Berechtigungsbedarf

Der Updater benötigt keine LAN-IP-Adresse und keinen festen Installationspfad. Er kommuniziert über den internen Supervisor-Dienst `http://supervisor` und die von Home Assistant bereitgestellte Variable `SUPERVISOR_TOKEN`.

Die App-Metadaten weisen dem Updater die Supervisor-Manager-Rolle zu. Diese Berechtigung wird benötigt, um den Store neu zu laden und das Update der Ziel-App anzufordern.

## Protokoll prüfen

Im Updater-Protokoll werden unter anderem ausgegeben:

- Start und Prüfintervall
- erkannte Ziel-App und Supervisor-Slug
- installierte Version und verfügbare Store-Version
- Ergebnis der Updateprüfung
- Ergebnis eines angeforderten Updates

Beispiel für einen Zustand ohne verfügbares Update:

```text
[Heliobridge Updater] Updater gestartet. Prüfintervall: 12 Stunde(n).
[Heliobridge Updater] Ziel-App: Heliobridge (d166b643_heliobridge)
[Heliobridge Updater] Installiert: 0.9.1.1; Repository: 0.9.1.1
[Heliobridge Updater] Heliobridge ist aktuell; kein Update erforderlich.
```

## Teststatus und Grenzen

Der Updater wurde auf einer HAOS-Installation gestartet. Das Protokoll hat die Ziel-App erkannt und den Versionsvergleich bei identischer installierter und verfügbarer Version erfolgreich durchgeführt.

Ein vollständiger Versionssprung mit einer neueren Upstream-Version und der anschließenden Installation durch den Supervisor ist noch nicht als Ende-zu-Ende-Test nachgewiesen. Ein erfolgreicher Versionsvergleich ohne Update ersetzt diesen Integrationstest nicht.

Ein erfolgreiches GitHub-Actions-Synchronisierungsergebnis bedeutet außerdem zunächst nur, dass die Upstream-Version geprüft bzw. in das Repository übernommen wurde. Der HAOS-Supervisor muss die neue App-Version anschließend im Store erkennen können.

## Fehlerdiagnose

- **Ziel-App nicht gefunden:** Den vollständigen Supervisor-Slug in `app_slug` prüfen.
- **Keine neue Store-Version:** Den GitHub-Actions-Workflow und anschließend die Aktualisierung des HAOS-App-Stores prüfen.
- **Update wird nicht angefordert:** `auto_update` und den Updater-Log prüfen.
- **Backup oder Supervisor-Update schlägt fehl:** Supervisor-Protokoll und verfügbaren Speicherplatz prüfen.
