from django.shortcuts import render
from django.http import HttpResponse
from jchart.config import Axes, DataSet, rgba
from jchart import Chart
from datetime import datetime, timedelta
from .print_chart import *
from .serializers import MitempSerializer
from rest_framework import views
from rest_framework.response import Response

#for auth:
from django.contrib.auth.decorators import login_required


class MitempApiView(views.APIView):
	'''API'''
	def get(self, request):
		'''readlast() provides list of dicts, in this case one dict in list, with recent 
		temperature/humidity etc, that is serialized for API'''
		results = MitempSerializer(readlast(), many=True).data
		return Response(results)


#@login_required
def site(request):
	'''Main view'''
	#if date is sent via form
	if request.method == 'POST':															
		StartDate = request.POST['StartDate']   				#retrive vars from forms
		EndDate = request.POST['EndDate']
		try: 													#input string verification
			datetime.strptime(StartDate , '%Y-%m-%d')
			datetime.strptime(EndDate, '%Y-%m-%d')
		except ValueError:
			StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
			EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")
			
			
		return render(request, 'temperature_sensor/index.html', 
		{
		'line_chart': LineChartInit(StartDate,EndDate).run_LineChart(),
		'StartDate': StartDate,
		'EndDate' : EndDate,
		})


	#no date set
	else:
		StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
		EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")
		return render(request, 'temperature_sensor/index.html', 
		{
		'line_chart': LineChartInit(StartDate,EndDate).run_LineChart(),
		'StartDate': StartDate,
		'EndDate' : EndDate,
		})

