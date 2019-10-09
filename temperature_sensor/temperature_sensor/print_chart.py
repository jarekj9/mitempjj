import mysql.connector as mariadb
from jchart.config import Axes, DataSet, rgba
from jchart import Chart
import collections
import statistics
from datetime import datetime, timedelta

g_startdate=""
g_enddate=""
#only takes date, sets global vars and starts LineChart(), which next uses these global vars
class LineChartInit:
	def __init__(self,StartDate,EndDate):
		global g_startdate,g_enddate
		g_startdate = StartDate
		g_enddate = EndDate
	def run_LineChart(self):
		return LineChart()


#all charts in one
class LineChart(Chart):
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
		
#read credentials for database connection
def config():
	addr,name,login,passw,mac="","","","",""
	with open ('.mitempjj','r') as file:
		lines = file.readlines()
	for line in lines:
		if 'db_address=' in line:  addr = line.split('db_address=')[1].strip()
		if 'db_name=' in line:     name = line.split('db_name=')[1].strip()
		if 'db_login=' in line:    login = line.split('db_login=')[1].strip()
		if 'db_password=' in line: passw = line.split('db_password=')[1].strip()
		if 'sensor_MAC=' in line:  mac = line.split('sensor_MAC=')[1].strip()
	
	return {'addr':addr,
			'name':name,
			'login':login,
			'passw':passw,
		    'mac':mac}
				
#read values from mariadb
def readall(**kwargs):
	if kwargs:
		StartDate= kwargs.get('StartDate')
		EndDate= kwargs.get('EndDate')
	else:#not used
		StartDate = (datetime.now() - timedelta(2) ).strftime("%Y-%m-%d")
		EndDate = datetime.now().strftime("%Y-%m-%d")
	
	datetab,batterytab,temperaturetab,humiditytab=[],[],[],[]
	mariadb_connection = mariadb.connect(host='172.19.0.1',user=config().get('login'), password=config().get('passw'), database=config().get('name'))
	cursor = mariadb_connection.cursor()
	cursor.execute("SELECT date,battery,temperature,humidity FROM temperature_sensor WHERE date BETWEEN CAST('%s' AS DATE) AND CAST('%s' AS DATE)" % (StartDate,EndDate))
	
	for date,battery,temperature,humidity in cursor:
		datetab.append(date)
		batterytab.append(battery)
		temperaturetab.append(temperature)
		humiditytab.append(humidity)

	mariadb_connection.close()			
	print(datetab)
	return {'datetab':datetab,
			'batterytab':batterytab,
			'temperaturetab':temperaturetab,
			'humiditytab':humiditytab}











