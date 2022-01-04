#!/usr/bin/env python3

from __future__ import annotations
from bluepy.btle import Scanner, DefaultDelegate, BTLEInternalError
import json
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SensorReading:
    '''Keep single sensor values'''
    mac: string = False
    temperature: float = False
    humidity: float = False
    battery: float = False
    battery_volt: int = False
    rssi: int = False


class SensorDataParser:
    @staticmethod
    def is_data_valid(data):
        '''Test if sensor provided bad readings'''
        if not(-50 < data.temperature < 100):
            return False
        elif not(0 < data.humidity < 100):
            return False
        elif not(2 < data.battery_volt < 4):
            return False
        else:
            return True
    @staticmethod
    def parseData(val, rssi=False):
        bytes = [int(val[i:i+2], 16) for i in range(0, len(val), 2)]
        return SensorReading(
            mac = ":".join(["{:02X}".format(bytes[i]) for i in range(2,8)]),
            temperature = (bytes[8] * 256 + bytes[9]) / 10,
            humidity = bytes[10],
            battery = bytes[11],
            battery_volt = (bytes[12] * 256 + bytes[13]) / 1000,
            rssi = rssi
        )


class ScanDelegate(DefaultDelegate):
    def __init__(self, mac):
        DefaultDelegate.__init__(self)
        self.mac = mac.lower()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        for (sdid, desc, val) in dev.getScanData():
            if self.isGoodMac(dev.addr, sdid, val) and SensorDataParser.is_data_valid(SensorDataParser.parseData(val)):
                return val

    def isGoodMac(self, addr, sdid, val):
        if addr == self.mac:
            return True
        return False


class FlashedDeviceScanner:
    def __init__(self, mac):
        self.mac = mac.lower()
        scanner = Scanner().withDelegate(ScanDelegate(self.mac))
        self.devices = scanner.scan(10.0, passive=True)
        while not self.isReadingValid():
            self.devices = scanner.scan(10.0, passive=True)

    def read(self):
        for dev in self.devices:
            if dev.addr == self.mac.lower():
               adtype, desc, value = dev.getScanData()[0]
               return SensorDataParser.parseData(value, dev.rssi)

    def isReadingValid(self):
        for dev in self.devices:
            if dev.addr == self.mac.lower():
               adtype, desc, value = dev.getScanData()[0]
               return SensorDataParser.is_data_valid(SensorDataParser.parseData(value))


if __name__ == '__main__':
    # test:
    scanner = FlashedDeviceScanner('A4:C1:38:F6:0A:5E')
    print(scanner.read())
