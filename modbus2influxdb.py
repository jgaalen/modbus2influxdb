#!/usr/bin/env python
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from influxdb import InfluxDBClient
import time
import requests

### INTERVAL
INTERVAL_MS=1000
INTERVAL_NODATA_MS=60000

### SMA MODBUS PARAMETERS
SMA_HOST="192.168.x.x"
SMA_PORT=502
UNIT_ID=3

### CONSOLE
VALUES_TO_CONSOLE=False

### INFLUXDB PARAMETERS
INFLUX_ENABLED=True
INFLUX_HOST="127.0.0.1"
INFLUX_PORT=8086
INFLUX_USER=""
INFLUX_PASSWORD=""
INFLUX_DATABASE="solar"
MEASUREMENT_NAME="Solar"
INVERTER_NAME="SMA"

### DOMOTICZ PARAMETERS
DOMOTICZ_ENABLED = True
DOMOTICZ_PROTOCOL = 'http'
DOMOTICZ_HOST = '127.0.0.1'
DOMOTICZ_PORT = 8080
DOMOTICZ_USERNAME = ''
DOMOTICZ_PASSWORD = ''

class device_info:
    def __init__(self, address, name, divisor, decimals, idx):
        self.address = address     # Modbux address
        self.name = name           # InfluxDB field name
        self.divisor = divisor     # Divisor of the value
        self.decimals = decimals   # How many decimals we want
        self.idx = idx             # idx domoticz id. 0 means it won't push it to domoticz

TOTAL_PROD       = device_info(30529, "total_yield", 1000, 3, 0)
DAY_PROD         = device_info(30535, "day_yield", 1000, 3, 0)
INVERTER_USAGE   = device_info(30581, "total_inverter_yield", 1000, 3, 0)
DC_AMP_A         = device_info(30769, "DC_Amps_A", 1000, 3, 0)
DC_VOLT_A        = device_info(30771, "DC_Volt_A", 100, 2, 739)
DC_WATT_A        = device_info(30773, "DC_Watt_A", 1, 0, 0)
AC_WATT          = device_info(30775, "AC_Watt", 1, 0, 710)
AC_WATT_L1       = device_info(30777, "AC_Watt_L1", 1, 1, 0)
AC_WATT_L2       = device_info(30779, "AC_Watt_L2", 1, 1, 0)
AC_WATT_L3       = device_info(30781, "AC_Watt_L3", 1, 1, 0)
VOLTAGE_L1       = device_info(30783, "AC_Volt_L1", 100, 2, 0)
VOLTAGE_L2       = device_info(30785, "AC_Volt_L2", 100, 2, 0)
VOLTAGE_L3       = device_info(30787, "AC_Volt_L3", 100, 2, 0)
GRID_FREQUENCY   = device_info(30803, "AC_net_Frequency", 100, 2, 0)
AC_R_POWER_L1    = device_info(30807, "AC_R_Power_L1", 1, 0, 0)
AC_R_POWER_L2    = device_info(30809, "AC_R_Power_L2", 1, 0, 0)
AC_R_POWER_L3    = device_info(30811, "AC_R_Power_L3", 1, 0, 0)
AC_A_POWER_L1    = device_info(30815, "AC_A_Power_L1", 1, 0, 0)
AC_A_POWER_L2    = device_info(30817, "AC_A_Power_L2", 1, 0, 0)
AC_A_POWER_L3    = device_info(30819, "AC_A_Power_L3", 1, 0, 0)
TEMPERATURE      = device_info(30953, "Temp", 10, 1, 0)
DC_AMP_B         = device_info(30957, "DC_Amps_B", 1000, 3, 0)
DC_VOLT_B        = device_info(30959, "DC_Volt_B", 100, 2, 740)
DC_WATT_B        = device_info(30961, "DC_Watt_B", 1, 0, 0)
AMP_L1           = device_info(30977, "AC_Amps_L1", 1000, 3, 0)
AMP_L2           = device_info(30979, "AC_Amps_L2", 1000, 3, 0)
AMP_L3           = device_info(30981, "AC_Amps_L3", 1000, 3, 0)
LEAK_AMP         = device_info(31247, "leakage", 1000, 3, 0)

devices = [TOTAL_PROD, DAY_PROD, DC_AMP_A, DC_VOLT_A, DC_WATT_A, AC_WATT,
           AC_WATT_L1, AC_WATT_L2, AC_WATT_L3, VOLTAGE_L1, VOLTAGE_L2, VOLTAGE_L3,
           GRID_FREQUENCY, AC_R_POWER_L1, AC_R_POWER_L2, AC_R_POWER_L3, AC_A_POWER_L1, AC_A_POWER_L2, AC_A_POWER_L3,
           TEMPERATURE, DC_AMP_B, DC_VOLT_B, DC_WATT_B, AMP_L1, AMP_L2, AMP_L3, LEAK_AMP]

U32_NAN = 0xFFFFFFFF
S32_NAN = 0x80000000

def connectModbus():
    try:
        global modbusClient
        modbusClient = ModbusClient(host=SMA_HOST, port=SMA_PORT)
        modbusClient.connect()
        print("Connected to inverter")
    except:
        print("Inverter modbus connection problem")

def connectInfluxDB():
    try:
        global influxDBClient
        influxDBClient = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASSWORD, INFLUX_DATABASE)
    except:
        print("InfluxDB connection problem")

def connectDomoticz():
    global domoticzClient
    domoticzClient = requests.Session()

def getModbusValues(start, count):

    if not modbusClient.is_socket_open():
        try:
            print("Connecting to inverter")
            modbusClient.connect()
        except:
            print("Inverter connection problem");
            return

    result = modbusClient.read_holding_registers(start, count, unit=UNIT_ID)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)

    for register in range(start, start + count, 2):
        decodedList[str(register)] = decoder.decode_32bit_uint()

    return decodedList

def getRegisterList():
    global valuesList
    valuesList = {}

    global decodedList
    decodedList = {}

    getModbusValues(30529, 54)
    getModbusValues(30769, 52)
    getModbusValues(30953, 30)
    getModbusValues(31247, 2)

    for device in devices:
        value = round(decodedList[str(device.address)] / device.divisor, device.decimals)
        if (("Volt" in device.name or "Temp" in device.name or "Frequency" in device.name) \
                and (decodedList[str(device.address)] == U32_NAN or decodedList[str(device.address)] == S32_NAN)):
            value = None
        elif (decodedList[str(device.address)] == S32_NAN or decodedList[str(device.address)] == U32_NAN):
            value = 0
        valuesList[device.name] = value

    if (VALUES_TO_CONSOLE):
        for name, value in valuesList.items():
            print(name + "\t" + str(value))

def sendToInfluxDB():
    json_body = [
        {
            "measurement": MEASUREMENT_NAME ,
            "tags": {
                "host": INVERTER_NAME
            },
            "fields": valuesList
        }
    ]
    try:
        influxDBClient.write_points(json_body)
    except:
        print("InfluxDB connection was lost")
        connectInfluxDB()
        influxDBClient.write_points(json_body)

def sendToDomoticz():
    try:
        for device in devices:
            if (device.idx != 0):
                value = str(valuesList[device.name])
                if (device == AC_WATT):
                    value += ';' + str(valuesList[TOTAL_PROD.name])
                url = DOMOTICZ_PROTOCOL + '://' + DOMOTICZ_USERNAME + ':' + DOMOTICZ_PASSWORD + '@' + \
                      DOMOTICZ_HOST + ':' + str(DOMOTICZ_PORT) + '/json.htm'
                params = {
                    'type': 'command',
                    'param': 'udevice',
                    'idx': str(device.idx),
                    'nvalue': '0',
                    'svalue': value,
                }
                domoticzClient.get(url, params=params)
    except:
        print("Domoticz connection problem")

if __name__ == "__main__":

    connectModbus()
    if INFLUX_ENABLED: connectInfluxDB()
    if DOMOTICZ_ENABLED: connectDomoticz()

    next_poll = (time.time() * 1000)
    while True:
        try:
            next_poll += INTERVAL_MS

            getRegisterList()
            if(valuesList[DC_VOLT_A.name] == None and valuesList[DC_VOLT_B.name] == None):
                next_poll += INTERVAL_NODATA_MS - INTERVAL_MS
            sleep_time = max((next_poll - (time.time() * 1000)) / 1000, 0)
            if (sleep_time == 0):
                next_poll = (time.time() * 1000)

            if INFLUX_ENABLED: sendToInfluxDB()
            if DOMOTICZ_ENABLED: sendToDomoticz()

            time.sleep(sleep_time)
        except KeyboardInterrupt:
            break
        except:
            time.sleep(sleep_time)
