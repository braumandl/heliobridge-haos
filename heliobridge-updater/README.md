# Heliobridge Updater

Der Updater installiert neue Heliobridge-Versionen, die der Originalautor
Simon Eisenmann unter `longsleep/heliobridge` veröffentlicht.

## Automatische Release-Kette

1. GitHub Actions dieses Repositorys prüft alle sechs Stunden das neueste stabile
   GitHub-Release von `longsleep/heliobridge`.
2. Bei einer neuen Version werden Original-Source und Versionsmetadaten automatisch
   in dieses HAOS-Paket übernommen und per GitHub Actions committed.
3. Der Home-Assistant-Supervisor erhält beim nächsten Store-Reload die neue App-Version.
4. Dieser Updater lädt den Store neu, erkennt die neue Version und fordert das reguläre
   Supervisor-Update an.
5. Vor dem Update wird standardmäßig ein Supervisor-Backup angefordert.

Du musst neue Upstream-Releases nicht manuell herunterladen oder in GitHub hochladen.

## Installation und Konfiguration

Installiere Heliobridge und anschließend Heliobridge Updater aus demselben Repository.
Der Updater benötigt Supervisor-Manager-Rechte.

Standardwerte:
- `app_name`: `Heliobridge`
- `app_slug`: leer (automatische Erkennung, sofern genau eine passende App installiert ist)
- `check_interval_hours`: `12`
- `backup_before_update`: `true`
- `auto_update`: `true`

Wenn mehrere Heliobridge-Installationen vorhanden sind, muss `app_slug` auf den
vollständigen Supervisor-Slug der gewünschten Instanz gesetzt werden.

## Netzwerk/IP-Unabhängigkeit

Der Updater benötigt keine LAN-IP-Adresse und keinen festen Installationspfad.
Er kommuniziert über den internen Supervisor-Dienst `http://supervisor` und die
von Home Assistant bereitgestellte `SUPERVISOR_TOKEN`-Variable.

## Grenzen und Sicherheit

- Es werden nur stabile, veröffentlichte Upstream-Releases gespiegelt.
- Die GitHub-Automation prüft Release-Tag und `Cargo.toml`-Version auf Übereinstimmung.
- Die HAOS-App-Paketversion wird aus der Upstream-Version als `<version>.1` gebildet.
- Vor dem Supervisor-Update wird standardmäßig ein Backup angefordert.
- Bei nicht eindeutiger App-Erkennung wird kein Update ausgeführt.
- Ein Upstream-Release wird erst nach erfolgreichem GitHub-Actions-Lauf im HAOS-Store sichtbar.
- Die automatische Aktualisierung setzt voraus, dass GitHub Actions im Repository aktiviert ist
  und die Workflow-Berechtigung `contents: write` besitzt.

## Teststatus

Die Shell-Syntax und der Python-Synchronisationscode müssen vor der Veröffentlichung
statisch geprüft werden. Ein echter Release-Sync und ein echter HAOS-Updateablauf sind
separate Integrationstests und werden nicht durch Syntaxprüfungen ersetzt.


The default `app_slug` targets the Heliobridge app in the `braumandl/heliobridge-haos` repository (`d166b643_heliobridge`). Change it only if your Supervisor shows a different slug for that repository installation.
