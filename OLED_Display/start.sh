#!/usr/bin/env bashio

set -e

bashio::log.info "Starting OLED display..."

if ls /dev/i2c-1; then 
    bashio::log.info "I2C access OK"
    bashio::log.info "Displaying info on OLED"
    cd /SSD1306OLED/
    python3 stats.py --mode hassio
else
    bashio::log.info "No I2C access."
fi