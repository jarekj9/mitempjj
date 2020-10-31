from jchart.config import Axes, DataSet, rgba
from jchart import Chart
import collections
import statistics
from datetime import datetime, timedelta
import sqlite3

g_startdate=""
g_enddate=""
SQLITE_DB_PATH = "./../database/mitempjj.db"

#only takes date, sets global vars and starts LineChart(), which next uses these global vars
class LineChartInit:
  def __init__(self,StartDate,EndDate):
    global g_startdate,g_enddate
    g_startdate = StartDate
    g_enddate = EndDate
  def run_LineChart(self):
    return LineChart()

class LineChart(Chart):
  '''All charts in one'''
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
      'data': readall(StartDate=g_startdate,EndDate=g_enddate).get('batterytab')},
    {
      'label': ["Temperature"],
      'data': readall(StartDate=g_startdate,EndDate=g_enddate).get('temperaturetab')},
    {
      'label': ["Humidity"],
      'data': readall(StartDate=g_startdate,EndDate=g_enddate).get('humiditytab')},
    
    ]
    
    
  def get_labels(self, **kwargs):
    return readall(StartDate=g_startdate,EndDate=g_enddate).get('datetab')    
    

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
    StartDate= kwargs.get('StartDate')
    EndDate= kwargs.get('EndDate')
  else:#not used
    StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
    EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")
  
  datetab,batterytab,temperaturetab,humiditytab=[],[],[],[]
  
  base=SQLITE(SQLITE_DB_PATH)
  sql_select = "SELECT date,battery,temperature,humidity from mitempjj WHERE date >= '%s' and date <= '%s';"%(StartDate,EndDate)
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


def readlast():
  '''Read last value from database'''
  base=SQLITE(SQLITE_DB_PATH)
  sql_select = "SELECT date,battery,temperature,humidity from mitempjj ORDER BY date DESC LIMIT 1;"
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

