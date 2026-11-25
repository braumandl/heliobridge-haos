#!/usr/bin/with-contenv bashio
set -Eeuo pipefail

readonly SUPERVISOR="http://supervisor"
readonly LOCK_DIR="/data/heliobridge-updater.lock"
log() { echo "[Heliobridge Updater] $*"; }

api_get() {
  curl -fsS --retry 2 --retry-delay 2 \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    "${SUPERVISOR}$1"
}
api_post() {
  curl -fsS --retry 2 --retry-delay 2 -X POST \
    -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
    -H "Content-Type: application/json" -d "$2" \
    "${SUPERVISOR}$1"
}
ok() {
  jq -e '.result == "ok"' >/dev/null <<<"$1"
}

discover_slug() {
  local configured="$1" name="$2" apps matches count
  if [[ -n "$configured" ]]; then
    printf '%s' "$configured"
    return
  fi
  apps="$(api_get "/addons")" || return 1
  ok "$apps" || return 1
  matches="$(jq -r --arg name "$name" '[.data.addons[]? | select(.name == $name) | .slug] | unique | .[]' <<<"$apps")"
  count="$(printf '%s\n' "$matches" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [[ "$count" != "1" ]]; then
    log "FEHLER: Genau eine installierte App namens '${name}' erwartet, gefunden: ${count}."
    log "Bei mehreren Installationen app_slug in den Optionen explizit setzen."
    return 1
  fi
  printf '%s' "$matches"
}

check_and_update() {
  local app_name slug info store installed latest state update_available
  app_name="$(bashio::config 'app_name')"
  slug="$(discover_slug "$(bashio::config 'app_slug')" "$app_name")" || return 1
  log "Ziel-App: ${app_name} (${slug})"

  # Reload the configured repositories so newly mirrored upstream releases are visible.
  store="$(api_post "/store/reload" "{}")" || {
    log "FEHLER: App-Store konnte nicht aktualisiert werden."
    return 1
  }
  ok "$store" || { log "FEHLER: Store-Reload: ${store}"; return 1; }

  info="$(api_get "/addons/${slug}/info")" || return 1
  ok "$info" || { log "FEHLER: App-Info: ${info}"; return 1; }
  installed="$(jq -er '.data.version' <<<"$info")" || return 1

  store="$(api_get "/store/addons/${slug}")" || return 1
  ok "$store" || { log "FEHLER: Store-Info: ${store}"; return 1; }
  latest="$(jq -er '.data.version_latest' <<<"$store")" || return 1
  update_available="$(jq -r '.data.update_available // false' <<<"$store")"

  log "Installiert: ${installed}; Repository: ${latest}"
  if [[ "$installed" == "$latest" || "$update_available" != "true" ]]; then
    log "Heliobridge ist aktuell; kein Update erforderlich."
    return 0
  fi

  if [[ "$(bashio::config 'auto_update')" != "true" ]]; then
    log "Neue Version vorhanden, automatische Updates sind deaktiviert."
    return 0
  fi

  local backup timeout
  backup="$(bashio::config 'backup_before_update')"
  log "Starte Supervisor-Update auf ${latest}; Backup=${backup}."
  store="$(api_post "/store/addons/${slug}/update" "{\"backup\":${backup},\"background\":false}")" || {
    log "FEHLER: Supervisor-Update fehlgeschlagen."
    return 1
  }
  ok "$store" || { log "FEHLER: Update-Antwort: ${store}"; return 1; }

  info="$(api_get "/addons/${slug}/info")" || return 1
  ok "$info" || return 1
  installed="$(jq -er '.data.version' <<<"$info")" || return 1
  state="$(jq -er '.data.state' <<<"$info")" || return 1
  if [[ "$installed" == "$latest" && "$state" == "started" ]]; then
    log "ERFOLG: Heliobridge ${installed} aktualisiert und gestartet."
    return 0
  fi

  log "FEHLER: Updateauftrag beendet, aber Version/Status nicht bestätigt (Version=${installed}, Status=${state})."
  return 1
}

run_check() {
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    log "Updateprüfung übersprungen: Sperre vorhanden."
    return 1
  fi
  local status=0
  check_and_update || status=$?
  rmdir "$LOCK_DIR" || log "WARNUNG: Sperre konnte nicht entfernt werden."
  return "$status"
}

[[ -n "${SUPERVISOR_TOKEN:-}" ]] || { log "FEHLER: SUPERVISOR_TOKEN fehlt."; exit 1; }
interval="$(bashio::config 'check_interval_hours')"
log "Updater gestartet. Prüfintervall: ${interval} Stunde(n)."
while true; do
  run_check || log "Updateprüfung fehlgeschlagen; nächster Versuch im konfigurierten Intervall."
  sleep "$((interval * 3600))"
done
