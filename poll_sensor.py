#!/usr/bin/env python3

from __future__ import annotations
import sys
import json
import argparse
import re
import logging
from logging.handlers import RotatingFileHandler
import sys
import subprocess
import sqlite3
from datetime import datetime
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from btlewrap.base import BluetoothBackendException
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
  MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY

from poll_square_flashed_sensor import FlashedDeviceScanner, SensorReading

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('logfile.log', maxBytes=10000000, backupCount=0)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class SQLITE():
  def __init__(self,db_file):
    self.conn = None
    try:
      self.conn = sqlite3.connect(db_file)
      self.c = self.conn.cursor()
    except sqlite3.Error as e:
      print(e)

  def sqlite_cmd(self,sqlite_cmd):
    try: 
      self.c.execute(sqlite_cmd)
    except sqlite3.Error as e:
      print(e)

  def sqlite_select(self,sqlite_cmd):
    try:
      self.c.execute(sqlite_cmd)
      output = [row for row in self.c]
      return(output)
    except sqlite3.Error as e:
      print(e)
    
  def sqlite_close(self):
    try:
      self.conn.commit()
      self.conn.close()
    except sqlite3.Error as e:
      print(e)

#this part is rebuilt from mitemp_bt demo script https://github.com/ratcashdev/mitemp
###################################################################################################
def valid_mitemp_mac(mac, pat=re.compile(r"4C:65:A8:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
  """Check for valid mac adresses."""
  if not pat.match(mac.upper()):
    raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
  return mac


def poll(args):
  """Poll data from the sensor."""
  backend = _get_backend(args)
  poller = MiTempBtPoller(args.mac, backend)
  print("Getting data from OLD ROUND Mi Temperature and Humidity Sensor")
  print(poller.parameter_value(MI_BATTERY),
         poller.parameter_value(MI_TEMPERATURE),
         poller.parameter_value(MI_HUMIDITY))
  return (poller.parameter_value(MI_BATTERY),
         poller.parameter_value(MI_TEMPERATURE),
         poller.parameter_value(MI_HUMIDITY))


def _get_backend(args):
  """Extract the backend class from the command line arguments."""
  if args.backend == 'gatttool':
    backend = GatttoolBackend
  elif args.backend == 'bluepy':
    backend = BluepyBackend
  elif args.backend == 'pygatt':
    backend = PygattBackend
  else:
    raise Exception('unknown backend: {}'.format(args.backend))
  return backend


def list_backends(_):
  """List all available backends."""
  backends = [b.__name__ for b in available_backends()]
  print('\n'.join(backends))

###################################################################################################

#read mac from file
def get_mac():
  macs = {'OLD_ROUND': {}, 'SMALL_SQUARE': {}}
  addr,name,login,passw,mac="","","","",""
  with open ('mac-address.txt','r') as file:
    lines = file.readlines()
  for line in lines:
    if line[0] == '#':
      continue
    if 'SENSOR_MAC_OLD_ROUND=' in line:
        mac = line.split('SENSOR_MAC_OLD_ROUND=')[1].split()[0].strip()
        name = line.split('SENSOR_MAC_OLD_ROUND=')[1].split()[1].strip()
        macs['OLD_ROUND'][name] = mac
    if 'SENSOR_MAC_SMALL_SQUARE=' in line:
        mac = line.split('SENSOR_MAC_SMALL_SQUARE=')[1].split()[0].strip()
        name = line.split('SENSOR_MAC_SMALL_SQUARE=')[1].split()[1].strip()
        macs['SMALL_SQUARE'][name] = mac
  return macs

def insert_into_db(name, mac, battery, temp, hum):
  base=SQLITE("./database/mitempjj.db")
  
  sql_create_table = """ CREATE TABLE IF NOT EXISTS mitempjj (
                                      id integer PRIMARY KEY AUTOINCREMENT,
                                      name text,
                                      mac text,
                                      date timestamp,
                                      battery float,
                                      temperature float,
                                      humidity float  
                                  ); """
  base.sqlite_cmd(sql_create_table)
  
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  sql_insert = "INSERT INTO mitempjj (date, name, mac, battery, temperature, humidity) VALUES \
                ('%s','%s','%s','%s',%s, %s);"%(timestamp, name, mac, battery, temp, hum)
  base.sqlite_cmd(sql_insert)
  base.sqlite_close()


def publish_mqtt(que, temperature, humidity):
    values = {
        "temperature": temperature,
        "humidity": humidity 
    }
    client = mqtt.Client()
    client.username_pw_set(username="pi",password="phalenopsis.6578")
    client.connect("localhost",1883,60, properties=None)
    client.publish(que, json.dumps(values), retain=True)
    client.disconnect()

def get_previous_values(mac: string) -> SensorReading:
    '''Get previous values from database for specific sensor'''
    previous_readings = SensorReading('', 0, 0, 0)
    base = SQLITE("./database/mitempjj.db")
    result = base.sqlite_select(f"SELECT mac, temperature, humidity, battery FROM mitempjj WHERE mac='{mac}' ORDER BY id DESC LIMIT 1;")
    if len(result):
        previous_readings = SensorReading(result[0][0], float(result[0][1]), float(result[0][2]), float(result[0][3]))
    return previous_readings

def main():
    for name, mac in get_mac().get('OLD_ROUND').items():
        parser = argparse.ArgumentParser()
        args = parser.parse_args()
        args.__dict__["mac"]=mac
        args.__dict__['verbose']=None
        args.__dict__['backend']='bluepy'
        battery, temp, hum = '', '', ''
        try: 
            battery,temp, hum = poll(args)
            print(battery,temp, hum)
        except BluetoothBackendException as e:
            logger.error(f'Problem occured when polling round sensor: {e}', exc_info=True)
            print(e)
        print(name, mac, battery, temp, hum )
        if temp:
            insert_into_db(name, mac, battery, temp, hum)
            #publish_mqtt("/home/living/tempsensor", temp, hum)

    for name, mac in get_mac().get('SMALL_SQUARE').items():
        print("Reading square sensor...")
        try:
            scanner = FlashedDeviceScanner(mac)
            sensor_value = scanner.read()
            print(f'Received correct square sensor values: {sensor_value}')
        except Exception as e:
            logger.error(f'Problem occured when polling square sensor: {e}', exc_info=True)
        if sensor_value.temperature:
            insert_into_db(name, mac, sensor_value.battery, sensor_value.temperature, sensor_value.humidity)
            #publish_mqtt("/home/hall/tempsensor", sensor_value.temperature, sensor_value.humidity)

if __name__=='__main__':
  main()




