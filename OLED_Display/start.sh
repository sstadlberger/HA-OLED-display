#!/usr/bin/env bashio

set -e

CONFIG_PATH=/data/options.json

DISABLE_AUTO_START="$(bashio::config 'Stop_Auto_Run')"
bashio::log.info "Starting OLED display..."
bashio::log.info "Disable Auto Start = ${DISABLE_AUTO_START}"


if [ "$DISABLE_AUTO_START" = false ]; then

    if ls /dev/i2c-1; then 
        bashio::log.info "I2C access OK";
        bashio::log.info "Displaying info on OLED"
        cd /SSD1306OLED/
        python3 display.py
    else
        bashio::log.info "No I2C access.";
    fi 

else
    bashio::log.info "No auto run"
    sleep 99999;
fi