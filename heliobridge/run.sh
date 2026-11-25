#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
set -euo pipefail

readonly STATE_DIR=/data/heliobridge

mkdir -p "${STATE_DIR}"
chown -R heliobridge:heliobridge "${STATE_DIR}"

MQTT_HOST="$(bashio::services mqtt 'host')"
MQTT_PORT="$(bashio::services mqtt 'port')"
MQTT_USER="$(bashio::services mqtt 'username')"
MQTT_PASSWORD="$(bashio::services mqtt 'password')"
MQTT_SSL="$(bashio::services mqtt 'ssl')"

case "${MQTT_SSL}" in
  true) MQTT_SCHEME=mqtts ;;
  *) MQTT_SCHEME=mqtt ;;
esac

export TZ="$(bashio::config 'timezone')"
export HELIOBRIDGE_LISTEN='0.0.0.0:7006'
export HELIOBRIDGE_STATE_DIR="${STATE_DIR}"
export HELIOBRIDGE_MQTT_URL="${MQTT_SCHEME}://${MQTT_HOST}:${MQTT_PORT}"
export HELIOBRIDGE_MQTT_USER="${MQTT_USER}"
export HELIOBRIDGE_MQTT_PASS="${MQTT_PASSWORD}"
export HELIOBRIDGE_MQTT_BASE="$(bashio::config 'mqtt_base')"
export HELIOBRIDGE_MQTT_DISCOVERY_PREFIX="$(bashio::config 'mqtt_discovery_prefix')"
export HELIOBRIDGE_ALLOW_WRITES="$(bashio::config 'allow_writes')"
export HELIOBRIDGE_ALLOW_POWER_PLUS="$(bashio::config 'allow_power_plus')"
export HELIOBRIDGE_CLOUD_RELAY="$(bashio::config 'cloud_relay')"
export HELIOBRIDGE_RELAY_MODE="$(bashio::config 'relay_mode')"
export HELIOBRIDGE_ALLOW_FROM="$(bashio::config 'allow_from')"
export HELIOBRIDGE_ALLOW_DEVICES="$(bashio::config 'allow_devices')"
export HELIOBRIDGE_SLOTS="$(bashio::config 'slots')"
export HELIOBRIDGE_OFFLINE_AFTER="$(bashio::config 'offline_after')"
export HELIOBRIDGE_LOG="$(bashio::config 'log_level')"
export HELIOBRIDGE_RECORD_DIR=''

bashio::log.info "Starting Heliobridge with Home Assistant MQTT service at ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Read-only mode: writes=${HELIOBRIDGE_ALLOW_WRITES}, power_plus=${HELIOBRIDGE_ALLOW_POWER_PLUS}, cloud_relay=${HELIOBRIDGE_CLOUD_RELAY}"

exec su-exec heliobridge:heliobridge /usr/local/bin/heliobridge
