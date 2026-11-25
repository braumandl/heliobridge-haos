# Heliobridge Updater – Betrieb

## GitHub Actions kontrollieren

Im GitHub-Repository unter **Actions** muss der Workflow
**Sync upstream Heliobridge release** sichtbar sein. Beim ersten Mal kann
**Run workflow** manuell ausgelöst werden.

Ein erfolgreicher Lauf ohne neue Version meldet `No upstream release change`.
Bei einer neuen Version muss der Workflow einen Commit mit der aktualisierten
Source und App-Version erzeugen.

## HAOS-Updater kontrollieren

Die Updater-Logs zeigen:
- erkannte Heliobridge-Instanz und Supervisor-Slug
- installierte Version und Store-Version
- ob ein Update nötig ist
- Ergebnis des Supervisor-Updateauftrags

## Häufige Fehler

- **Keine eindeutige Ziel-App:** `app_slug` manuell konfigurieren.
- **Keine neue Version im Store:** GitHub-Actions-Lauf und Repository-Synchronisierung prüfen.
- **Update fehlgeschlagen:** Supervisor-Protokoll und Heliobridge-App-Protokoll prüfen.
- **Backup fehlgeschlagen:** Update wird durch den Supervisor nicht als erfolgreich bestätigt;
  Backup-Option und freien Speicher prüfen.
