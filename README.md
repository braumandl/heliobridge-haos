# Heliobridge für Home Assistant OS

Dieses Repository stellt zwei eigenständige Home-Assistant-OS-Apps für den Betrieb der Growatt NEXA 2000 mit Home Assistant bereit:

1. **Heliobridge** – paketiert die Originalsoftware von Simon Eisenmann als HAOS-App. Sie nimmt die TLS-Verbindung des NEXA-Datenloggers entgegen und stellt die Daten über den Home-Assistant-MQTT-Dienst und MQTT Discovery bereit.
2. **Heliobridge Updater** – prüft den App-Store in regelmäßigen Abständen und kann eine neuere Heliobridge-App-Version über den Home Assistant Supervisor installieren.

Die eigentliche Heliobridge-Software wird von Simon Eisenmann entwickelt:
https://github.com/longsleep/heliobridge

Dieses Repository enthält die HAOS-Verpackung und die dazugehörige Update-Infrastruktur. Es ist ein unabhängiges Community-Projekt und weder ein offizielles Growatt-Produkt noch ein offizieller Bestandteil des Upstream-Projekts.

---

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Repository in Home Assistant hinzufügen](#repository-in-home-assistant-hinzufügen)
- [App 1: Heliobridge installieren](#app-1-heliobridge-installieren)
- [Heliobridge konfigurieren](#heliobridge-konfigurieren)
- [Netzwerkumleitung einrichten](#netzwerkumleitung-einrichten)
- [App 2: Heliobridge Updater installieren](#app-2-heliobridge-updater-installieren)
- [Wie die automatische Updatekette funktioniert](#wie-die-automatische-updatekette-funktioniert)
- [Fehlerdiagnose](#fehlerdiagnose)
- [Deinstallation](#deinstallation)
- [Versionen und technische Angaben](#versionen-und-technische-angaben)
- [Originalprojekt und Hinweise](#originalprojekt-und-hinweise)

## Voraussetzungen

- Home Assistant OS mit Supervisor.
- Home Assistant MQTT-Dienst, zum Beispiel Mosquitto, installiert und gestartet.
- Growatt NEXA 2000 mit Netzwerkverbindung.
- Netzwerkweg vom NEXA-Datenlogger zum Home-Assistant-Host auf TCP-Port `7006`.
- Derzeit ist in der App-Metadatei ausschließlich die Architektur `amd64` eingetragen.

## Repository in Home Assistant hinzufügen

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/braumandl/heliobridge-haos)

Alternativ manuell:

1. Home Assistant öffnen und zu **Einstellungen → Apps** wechseln.
2. Im App-Store das Menü oben rechts öffnen.
3. **Repositories** auswählen.
4. Folgende Adresse hinzufügen:

   `https://github.com/braumandl/heliobridge-haos`

5. Den App-Store aktualisieren.

Das Hinzufügen des Repositorys installiert die Apps noch nicht. **Heliobridge und Heliobridge Updater müssen jeweils separat installiert werden.**

## App 1: Heliobridge installieren

1. Im App-Store die App **Heliobridge** aus diesem Repository auswählen.
2. Installieren.
3. Vor dem Start die Konfiguration prüfen.
4. App starten.
5. Das App-Protokoll kontrollieren.

Die App verwendet den Home-Assistant-MQTT-Dienst. In den Protokollen sollte die Verbindung zum MQTT-Dienst erfolgreich aufgebaut werden. Der TLS-Listener für den NEXA-Datenlogger verwendet TCP-Port `7006`.

Ein erfolgreicher TCP-Listener allein weist noch keine Verbindung des NEXA-Datenloggers nach. Geräte und MQTT-Discovery-Entitäten erscheinen erst, wenn der Datenlogger tatsächlich eine Verbindung aufbaut und Daten liefert.

## Heliobridge konfigurieren

Die App-Optionen werden über die Konfigurationsoberfläche von Home Assistant verwaltet. Die aktuell in `heliobridge/config.yaml` definierten Optionen sind:

| Option | Standardwert | Bedeutung |
|---|---:|---|
| `allow_writes` | `false` | Erlaubt schreibende Steuerbefehle |
| `allow_power_plus` | `false` | Aktiviert Power+-Schreibfunktionen |
| `cloud_relay` | `false` | Aktiviert die Weiterleitung zur Growatt-Cloud |
| `relay_mode` | `controls` | Relay-Modus: `full`, `controls` oder `observer` |
| `allow_from` | leer | Optionale Liste erlaubter Quell-IP-Adressen/-Netze |
| `allow_devices` | leer | Optionale Liste erlaubter Geräte-Seriennummern |
| `slots` | `1` | Anzahl der bereitgestellten Zeitplan-Slots (1–9) |
| `offline_after` | `30` | Sekunden ohne Telemetrie bis ein Gerät als offline gilt |
| `mqtt_base` | `heliobridge` | MQTT-Basis-Topic |
| `mqtt_discovery_prefix` | `homeassistant` | MQTT-Discovery-Präfix |
| `timezone` | `Europe/Berlin` | Zeitzone |
| `log_level` | `info` | Protokollierungsstufe |

### Sicherheitshinweise zu den Standardwerten

Für die erste Inbetriebnahme bleiben die schreibenden Funktionen und das Cloud-Relay ausgeschaltet:

```yaml
allow_writes: false
allow_power_plus: false
cloud_relay: false
```

Die Optionen `allow_from` und `allow_devices` sind standardmäßig leer. **Im gebündelten Upstream-Code bedeutet eine leere Allowlist nicht „niemand ist erlaubt“, sondern es wird keine Einschränkung anhand dieser Liste vorgenommen.** Wer den Zugriff einschränken möchte, muss die Listen ausdrücklich konfigurieren.

Schreibfunktionen und Cloud-Relay nur aktivieren, wenn die Auswirkungen verstanden und die gewünschte Betriebsweise geprüft wurden.

## Netzwerkumleitung einrichten

Der NEXA-Datenlogger muss den lokalen Heliobridge-Listener erreichen können. Das Upstream-Projekt dokumentiert dafür zwei Ansätze:

- **DNS-Override:** Der Name `mqtt.growatt.com` wird im lokalen Netzwerk auf die IP-Adresse des Home-Assistant-Hosts aufgelöst.
- **Destination NAT:** Der entsprechende Datenverkehr wird auf den Home-Assistant-Host und TCP-Port `7006` weitergeleitet.

Die konkrete Einrichtung ist abhängig vom Router und der Netzwerktopologie. Diese HAOS-App richtet weder den DNS-Override noch die NAT-Regel selbst ein. Sie verändert auch keine NEXA-Endpoint-Register.

**Reihenfolge:** Zuerst Heliobridge installieren und starten. Danach prüfen, ob MQTT verbunden ist und TCP-Port `7006` lauscht. Erst anschließend die Netzwerkumleitung einrichten. Nach der Umleitung die eingehende Verbindung des NEXA-Datenloggers und die MQTT-Geräte in Home Assistant kontrollieren.

Zur Rückkehr zum normalen Cloud-Pfad die eingerichtete DNS-Umleitung bzw. Destination-NAT-Regel wieder entfernen.

## App 2: Heliobridge Updater installieren

Der Updater ist eine **separate, optionale App**. Das Hinzufügen des Repositorys oder die Installation der Heliobridge installiert den Updater nicht automatisch.

1. Im selben App-Repository die App **Heliobridge Updater** auswählen.
2. Separat installieren.
3. Starten.
4. Das Updater-Protokoll kontrollieren.

Der Updater benötigt Supervisor-Manager-Rechte, um den App-Store neu zu laden und eine App-Aktualisierung anzufordern.

### Updater-Optionen

Die aktuelle `heliobridge-updater/config.yaml` enthält:

| Option | Standardwert | Bedeutung |
|---|---:|---|
| `app_name` | `Heliobridge` | Name der Ziel-App |
| `app_slug` | `d166b643_heliobridge` | Vollständiger Supervisor-Slug der Ziel-App |
| `check_interval_hours` | `12` | Prüfintervall in Stunden |
| `backup_before_update` | `true` | Backup vor dem Update anfordern |
| `auto_update` | `true` | Verfügbare Updates automatisch anfordern |

Der konfigurierte Standard-Slug `d166b643_heliobridge` entspricht der Heliobridge-App aus diesem Repository. Bei abweichendem Repository-Slug oder einer anderen Zielinstallation muss der Wert geprüft und gegebenenfalls angepasst werden.

Der Updater kommuniziert intern über `http://supervisor` und die von Home Assistant bereitgestellte Variable `SUPERVISOR_TOKEN`. Eine feste LAN-IP-Adresse oder ein fester Installationspfad wird dafür nicht konfiguriert.

## Wie die automatische Updatekette funktioniert

Die Updatekette besteht aus zwei getrennten Schritten:

### 1. Originalquelle in dieses Repository übernehmen

Der GitHub-Actions-Workflow **Sync upstream Heliobridge release** läuft nach Zeitplan alle sechs Stunden und kann zusätzlich manuell gestartet werden.

Das Skript `scripts/sync-upstream.py`:

- fragt die Git-Tags des Originalprojekts über die GitHub-Tags-API ab,
- wählt den höchsten stabilen Tag im Format `X.Y.Z` bzw. `vX.Y.Z`,
- schließt Tags mit Vorabversionssuffix aus,
- lädt das Archiv des ausgewählten Tags,
- prüft, ob die Version in `Cargo.toml` mit dem Tag übereinstimmt,
- übernimmt den Quellcode und aktualisiert die HAOS-Paketversion.

Die HAOS-Paketversion wird derzeit nach dem Schema `<Upstream-Version>.1` gebildet. Bei Änderungen erzeugt der Workflow einen Commit in diesem Repository.

### 2. Neue App-Version in Home Assistant installieren

Der Heliobridge Updater lädt den Home-Assistant-App-Store neu, vergleicht installierte und verfügbare App-Version und fordert – wenn eine neuere Version verfügbar ist und `auto_update` aktiviert ist – das Supervisor-Update an. Standardmäßig wird dabei ein Backup angefordert.

Der GitHub-Synchronisierungsworkflow und der HAOS-Updater sind unabhängig voneinander. Die neue Version muss zuerst erfolgreich in dieses Repository übernommen und anschließend vom Supervisor im Store erkannt werden.

### Aktueller Teststatus

Die GitHub-Actions-Synchronisierung wurde mit dem vorhandenen Upstream-Tag `v0.9.1` ausgeführt. Der Workflow erkannte, dass diese Version bereits gespiegelt war und daher kein Commit notwendig war.

Der Updater wurde auf einer HAOS-Installation gestartet. Sein Protokoll bestätigte die Ziel-App `d166b643_heliobridge` sowie den Versionsvergleich `0.9.1.1` gegen `0.9.1.1` und meldete, dass kein Update erforderlich ist.

**Ein vollständiger Versionssprung mit neuer Upstream-Version und anschließendem Supervisor-Update ist damit noch nicht nachgewiesen.** Die automatische Updatekette sollte deshalb als implementiert, aber noch nicht vollständig durch einen Versionswechsel integrationstestet betrachtet werden.

## Fehlerdiagnose

### Heliobridge verbindet sich nicht mit MQTT

- Prüfen, ob der Home-Assistant-MQTT-Dienst installiert und gestartet ist.
- Heliobridge-Protokoll auf die MQTT-Verbindung prüfen.
- MQTT-Zugangsdaten bzw. den Supervisor-MQTT-Dienst prüfen.

### Keine Verbindung vom NEXA-Datenlogger

- DNS-Auflösung von `mqtt.growatt.com` bzw. Destination-NAT prüfen.
- Erreichbarkeit des Home-Assistant-Hosts auf TCP-Port `7006` prüfen.
- Heliobridge-Protokoll auf eingehende TLS-Verbindungen prüfen.

### Keine MQTT-Discovery-Entitäten

- Prüfen, ob der NEXA-Datenlogger tatsächlich verbunden ist und Telemetrie liefert.
- MQTT-Dienst und Discovery-Präfix kontrollieren.
- Heliobridge-Protokoll auf erfolgreiche MQTT-Publikation prüfen.

### Updater meldet keine neue Version

- GitHub Actions öffnen und den Lauf **Sync upstream Heliobridge release** prüfen.
- Sicherstellen, dass der Workflow erfolgreich abgeschlossen wurde.
- Prüfen, ob die aktualisierte App-Version im Home-Assistant-App-Store angezeigt wird.
- Updater-Protokoll auf Ziel-Slug und Versionsvergleich prüfen.

### Updater findet die Ziel-App nicht

Den vollständigen Supervisor-Slug der gewünschten Heliobridge-Installation in `app_slug` eintragen. Bei mehreren installierten Heliobridge-Apps nicht auf automatische Namenssuche vertrauen.

## Deinstallation

Die Apps können unabhängig voneinander entfernt werden.

- **Nur Updater deinstallieren:** Heliobridge läuft weiter; Updates müssen anschließend manuell über den App-Store installiert werden.
- **Heliobridge deinstallieren:** Zuerst die DNS- oder Destination-NAT-Umleitung zurücknehmen bzw. den Datenlogger wieder auf den gewünschten Netzwerkpfad bringen. Danach die App deinstallieren.

Vor einer Deinstallation oder größeren Änderung wird ein aktuelles Home-Assistant-Backup empfohlen.

## Versionen und technische Angaben

Aktuell im Repository:

- HAOS-App-Paketversion: `0.9.1.1`
- Gebündelte Upstream-Quellversion: `0.9.1`
- Architektur der Heliobridge-App: `amd64`
- TLS-Listener: TCP `7006`
- Persistenter Heliobridge-Zustand: `/data/heliobridge`

Die Heliobridge wird im Dockerfile aus dem gebündelten Rust-Quellcode gebaut. In der App-Konfiguration ist kein vorgebautes Image angegeben; der Supervisor baut die App daher beim Installieren aus dem Dockerfile.

Weitere technische Informationen:

- [Heliobridge-App-Dokumentation](heliobridge/DOCS.md)
- [Heliobridge-Changelog](heliobridge/CHANGELOG.md)
- [Build- und Verifizierungsstatus](heliobridge/BUILD-VERIFICATION.md)
- [Updater-Dokumentation](heliobridge-updater/DOCS.md)
- [Updater-README](heliobridge-updater/README.md)

## Originalprojekt und Lizenzhinweise

Die Heliobridge selbst stammt von Simon Eisenmann:

https://github.com/longsleep/heliobridge

Die Upstream-Urheberrechtsvermerke sowie die Lizenz- und NOTICE-Dateien bleiben im eingebundenen Quellcode erhalten. Bitte beachte die Lizenzbedingungen des Originalprojekts bei Weitergabe und Änderungen.

Dieses Repository ist unabhängig von Growatt. Growatt und NEXA sind Marken ihrer jeweiligen Rechteinhaber.
