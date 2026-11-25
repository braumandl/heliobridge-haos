# Heliobridge – Home Assistant OS App

[English](README.md) · [Deutsch](README.de.md)

Diese App paketiert die Originalsoftware [Heliobridge von Simon Eisenmann](https://github.com/longsleep/heliobridge) für Home Assistant OS.

Sie stellt eine lokale TLS-/MQTT-Bridge für den Growatt NEXA 2000 bereit und veröffentlicht Gerätedaten über den Home-Assistant-MQTT-Dienst und MQTT Discovery.

## Voraussetzungen

- Home Assistant OS mit Supervisor auf der in `config.yaml` aufgeführten Architektur `amd64`.
- Installierter und laufender Home-Assistant-MQTT-Dienst.
- Netzwerkverbindung vom NEXA-Datenlogger zum Home-Assistant-Host auf TCP-Port `7006`.

## Installation

1. Das Repository `https://github.com/braumandl/heliobridge-haos` zum Home-Assistant-App-Store hinzufügen.
2. Die App **Heliobridge** auswählen und installieren.
3. Konfiguration prüfen und App starten.
4. App-Protokoll auf MQTT-Verbindung und Start des TLS-Listeners prüfen.

Die Heliobridge Updater-App ist eine separate optionale App und muss bei Bedarf zusätzlich installiert werden.

## Optionen

| Option | Standardwert | Bedeutung |
|---|---:|---|
| `allow_writes` | `false` | Schreibende Steuerbefehle erlauben |
| `allow_power_plus` | `false` | Power+-Schreibfunktionen aktivieren |
| `cloud_relay` | `false` | Growatt-Cloud-Relay aktivieren |
| `relay_mode` | `controls` | Relay-Modus: `full`, `controls` oder `observer` |
| `allow_from` | leer | Optionale Quell-IP-/Netzwerk-Allowlist |
| `allow_devices` | leer | Optionale Allowlist von Geräte-Seriennummern |
| `slots` | `1` | Anzahl der Zeitplan-Slots (1–9) |
| `offline_after` | `30` | Sekunden ohne Telemetrie bis offline |
| `mqtt_base` | `heliobridge` | MQTT-Basis-Topic |
| `mqtt_discovery_prefix` | `homeassistant` | MQTT-Discovery-Präfix |
| `timezone` | `Europe/Berlin` | Zeitzone |
| `log_level` | `info` | Protokollierungsstufe |

### Sicherheitshinweise zu den Standardwerten

Die schreibenden Funktionen und das Cloud-Relay sind standardmäßig deaktiviert:

```yaml
allow_writes: false
allow_power_plus: false
cloud_relay: false
```

Leere Werte bei `allow_from` und `allow_devices` bedeuten im gebündelten Upstream-Code, dass anhand dieser Listen keine Einschränkung vorgenommen wird. Leere Listen sind daher keine Deny-all-Sperre.

## Netzwerkumleitung

Der NEXA-Datenlogger muss auf die lokale Bridge umgeleitet werden. Das Upstream-Projekt dokumentiert:

- DNS-Override für `mqtt.growatt.com` auf die IP-Adresse des Home-Assistant-Hosts, oder
- Destination-NAT auf den Home-Assistant-Host und TCP-Port `7006`.

Die App richtet diese Netzwerkregeln nicht selbst ein und verändert keine NEXA-Endpoint-Register. Richte DNS/NAT erst ein, nachdem die App startet und ihre MQTT-Verbindung erfolgreich hergestellt hat.

## Fehlerdiagnose

- MQTT-Verbindung im App-Protokoll kontrollieren.
- Prüfen, ob TCP-Port `7006` lauscht.
- Prüfen, ob der NEXA-Datenlogger tatsächlich eine TLS-Verbindung aufbaut.
- MQTT Discovery und das konfigurierte Discovery-Präfix kontrollieren.

Ein erfolgreicher TCP-Watchdog-Test bestätigt nur, dass der Listener erreichbar ist. Er beweist nicht, dass ein NEXA-Gerät verbunden ist oder gültige Telemetrie und MQTT-Discovery-Daten veröffentlicht werden.

## Zurück zur Growatt-Cloud

Die App stoppen und den eingerichteten DNS-Override für `mqtt.growatt.com` bzw. die Destination-NAT-Regel entfernen. Dieses Paket verändert keine NEXA-Endpoint-Register.
