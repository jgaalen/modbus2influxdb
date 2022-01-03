# Script for sending SMA Modbus data to InfluxDB and Domoticz

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
