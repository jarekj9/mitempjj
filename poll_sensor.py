#!/usr/bin/env python3

import argparse
import re
import logging
import sys
import subprocess
import mysql.connector as mariadb 
from datetime import datetime

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
  MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY

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
  print("Getting data from Mi Temperature and Humidity Sensor")
  print("FW: {}".format(poller.firmware_version()))
  print("Name: {}".format(poller.name()))

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


def print_data():
  parser = argparse.ArgumentParser()
  args = parser.parse_args()
  args.__dict__["mac"]='4c:65:a8:d4:b9:f0'
  args.__dict__['verbose']=None
  args.__dict__['backend']='bluepy'
  poll(args)

###################################################################################################


# create tables if they don't exist
def create_tables():
  #create DB if not exists
  mariadb_connection = mariadb.connect(user=config().get('login'), password=config().get('passw'), port=13306)
  cursor = mariadb_connection.cursor()
  cursor.execute("create database IF NOT EXISTS %s" % config().get('name') )
  mariadb_connection.commit()
  mariadb_connection.close()

  #create tables if not exist
  mariadb_connection = mariadb.connect(user=config().get('login'), password=config().get('passw'), database=config().get('name'), port=13306)
  cursor = mariadb_connection.cursor()
  try:
    cursor.execute("CREATE TABLE IF NOT EXISTS temperature_sensor("
    "no double NOT NULL AUTO_INCREMENT,"
    "date timestamp NOT NULL,"
    "battery int,"
    "temperature float,"
    "humidity float,"
    "PRIMARY KEY (no))")
  except mariadb.Error as error:
    print("Error: {}".format(error))
  mariadb_connection.commit()
  mariadb_connection.close()
  
  return True

#read credentials for database connection
def config():
  addr,name,login,passw,mac="","","","",""
  with open ('temperature_sensor/.mitempjj','r') as file:
    lines = file.readlines()
  for line in lines:
    if 'db_address=' in line:  addr = line.split('db_address=')[1].strip()
    if 'db_name=' in line:   name = line.split('db_name=')[1].strip()
    if 'db_login=' in line:  login = line.split('db_login=')[1].strip()
    if 'db_password=' in line: passw = line.split('db_password=')[1].strip()
    if 'sensor_MAC=' in line:  mac = line.split('sensor_MAC=')[1].strip()
  
  return {'addr':addr,
      'name':name,
      'login':login,
      'passw':passw,
      'mac':mac}

#write data into DB
def insert_into_db(battery,temp,hum):
  
  mariadb_connection = mariadb.connect(user=config().get('login'), password=config().get('passw'), database=config().get('name'), port=13306) 

  cursor = mariadb_connection.cursor()
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  cursor.execute("INSERT INTO temperature_sensor (date,battery,temperature,humidity) VALUES ('%s','%s','%s','%s')" % (timestamp,battery,float(temp),float(hum)))
  
  mariadb_connection.commit()
  print ("The last inserted id was: ", cursor.lastrowid)
  mariadb_connection.close()


def main():
  parser = argparse.ArgumentParser()
  args = parser.parse_args()
  args.__dict__["mac"]=config().get('mac')
  args.__dict__['verbose']=None
  args.__dict__['backend']='bluepy'
  
  battery,temp,hum = poll(args)
  #print(battery,temp,hum)
  #create_tables()
  insert_into_db(battery,temp,hum)

if __name__=='__main__':
  main()



