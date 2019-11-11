#!/usr/bin/env python3

import argparse
import re
import logging
import sys
import subprocess
import sqlite3
from datetime import datetime

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
  MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY

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

###################################################################################################

#read mac from file
def get_mac():
  addr,name,login,passw,mac="","","","",""
  with open ('mac-address.txt','r') as file:
    lines = file.readlines()
  for line in lines:
    if 'sensor_MAC=' in line:  mac = line.split('sensor_MAC=')[1].strip()
  
  return mac

#write data into DB
def insert_into_db(battery,temp,hum):
  base=SQLITE("./database/mitempjj.db")
  
  sql_create_table = """ CREATE TABLE IF NOT EXISTS mitempjj (
                                      id integer PRIMARY KEY AUTOINCREMENT,
                                      date timestamp,
                                      battery int,
                                      temperature float,
                                      humidity float  
                                  ); """
  base.sqlite_cmd(sql_create_table)
  
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  sql_insert = " INSERT INTO mitempjj (date,battery,temperature,humidity) VALUES \
                                      ('%s',%s,%s,%s);"%(timestamp,battery,temp,hum)
  base.sqlite_cmd(sql_insert)
  base.sqlite_close()
  
def main():
  parser = argparse.ArgumentParser()
  args = parser.parse_args()
  args.__dict__["mac"]=get_mac()
  args.__dict__['verbose']=None
  args.__dict__['backend']='bluepy'
  
  battery,temp,hum = poll(args)
  insert_into_db(battery,temp,hum)

if __name__=='__main__':
  main()




