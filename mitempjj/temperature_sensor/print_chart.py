from jchart.config import Axes, DataSet, rgba
from jchart import Chart
import collections
import statistics
from datetime import datetime, timedelta
import sqlite3


SQLITE_DB_PATH = "./../database/mitempjj.db"


class LineChart(Chart):
  '''All charts in one'''

  def __init__(self, start_date, stop_date, sensor_name):
      self.start_date = start_date
      self.stop_date = stop_date
      self.sensor_name = sensor_name
      super().__init__()
      

  chart_type = 'line'

  def get_datasets(self, **kwargs):
    colors = [
      rgba(255, 99, 132, 0.2),
      rgba(54, 162, 235, 0.2),
      rgba(255, 206, 86, 0.2),
      rgba(75, 192, 192, 0.2),
      rgba(153, 102, 255, 0.2),
      rgba(255, 159, 64, 0.2)
    ]
    return [
    {
      'label': ["Battery"],
      #'borderColor' : colors,
      #'backgroundColor' : colors,
      'data': readall(StartDate=self.start_date, EndDate=self.stop_date, sensor_name=self.sensor_name).get('batterytab')
    },
    {
      'label': ["Temperature"],
      'data': readall(StartDate=self.start_date, EndDate=self.stop_date, sensor_name=self.sensor_name).get('temperaturetab')
    },
    {
      'label': ["Humidity"],
      'data': readall(StartDate=self.start_date, EndDate=self.stop_date, sensor_name=self.sensor_name).get('humiditytab')
    },
    
    ]
    
    
  def get_labels(self, **kwargs):
    return readall(StartDate=self.start_date,EndDate=self.stop_date, sensor_name=self.sensor_name) .get('datetab')
    

class SQLITE():
  '''Usefull methods to handle sqlite commands'''
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
    


def readall(**kwargs):
  '''Read all values from sqlite'''
  if kwargs:
    StartDate = kwargs.get('StartDate')
    EndDate = kwargs.get('EndDate')
    sensor_name = kwargs.get('sensor_name')
  else:#not used
    StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
    EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")
  datetab,batterytab,temperaturetab,humiditytab=[],[],[],[]

  base=SQLITE(SQLITE_DB_PATH)
  sql_select = "SELECT date,battery,temperature,humidity from mitempjj WHERE date >= '%s' and date <= '%s' and name == '%s';"%(StartDate, EndDate, sensor_name)
  rows=base.sqlite_select(sql_select)
  base.sqlite_close()
  if rows:
    unzipped=list(zip(*rows))
    return {'datetab':unzipped[0],
        'batterytab':unzipped[1],
        'temperaturetab':unzipped[2],
        'humiditytab':unzipped[3]}
  else:
    return {'datetab':[0],
        'batterytab':[0],
        'temperaturetab':[0],
        'humiditytab':[0]}


def readlast(sensor_name):
  '''Read last value from database'''
  base=SQLITE(SQLITE_DB_PATH)
  sql_select = "SELECT date,battery,temperature,humidity from mitempjj WHERE name == '%s' ORDER BY date DESC LIMIT 1;"%(sensor_name)
  rows=base.sqlite_select(sql_select)
  base.sqlite_close()
  
  if rows:
    return [{'date':rows[0][0],
            'battery':rows[0][1],
            'temperature':rows[0][2],
            'humidity':rows[0][3]}]
  else:
    return [{'date':'0000-00-00',
            'battery':0,
            'temperature':0,
            'humidity':0}]

def get_sensor_names():
  '''Get list of sensor names from db'''
  base=SQLITE(SQLITE_DB_PATH)
  sql_select = "SELECT DISTINCT name from mitempjj;"
  rows=base.sqlite_select(sql_select)
  base.sqlite_close()
  return [tupl[0] for tupl in rows]
