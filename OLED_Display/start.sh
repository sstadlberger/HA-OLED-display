#!/usr/bin/env bashio

set -e

CONFIG_PATH=/data/options.json

bashio::log.info "Starting OLED display..."

if ls /dev/i2c-1; then 
    bashio::log.info "I2C access OK"
    bashio::log.info "Displaying info on OLED"
    bashio::log.info "Token:"
    bashio::log.info "$(bashio::config 'SUPERVISOR_TOKEN')"
    export SUPERVISOR_TOKEN="$(bashio::config 'SUPERVISOR_TOKEN')"
    bashio::log.info "Token is = ${SUPERVISOR_TOKEN}"
    cd /SSD1306OLED/
    python3 stats.py --mode hassio
else
    bashio::log.info "No I2C access."
fi