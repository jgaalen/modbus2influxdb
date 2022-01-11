# Script for sending SMA Modbus data to InfluxDB and Domoticz

This is a script for reading SMA values on a high interval (1 second). Because polling for single modbus data can take up to 150ms, polling for a bunch of data can take seconds. This script takes 250ms to poll up to 20 data points on newer models and about 650ms on older models.

It let's you push the data to InfluxDB and/or Domoticz

## Requirements
- Modbus enabled on your SMA inverter

## Installation
```bash
git clone https://github.com/jgaalen/modbus2influxdb.git
pip3 install -U pymodbus pymodbusTCP influxdb
```

## Tested on
- SMA STP5000TL-20
- SMA SB 3.6-1AV-41

## Thanks

Script is influenced by [(derenback)](https://github.com/derenback/Domoticz-SMA-Inverter)
