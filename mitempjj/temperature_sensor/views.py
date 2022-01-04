import logging
from django.shortcuts import render
from django.http import HttpResponse
from jchart.config import Axes, DataSet, rgba
from jchart import Chart
from datetime import datetime, timedelta
from .print_chart import *
from .print_chart2 import *
from .serializers import MitempSerializer
from rest_framework import views
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import redirect

#for auth:
from django.contrib.auth.decorators import login_required


logging.basicConfig(level=logging.INFO, filename='sample.log') 

SENSORS = get_sensor_names()

class MitempApiView(views.APIView):
    '''API'''
    def get(self, request):
        '''readlast() provides list of dicts, in this case one dict in list, with recent 
        temperature/humidity etc, that is serialized for API'''
        results = {}
        for sensor_name in SENSORS:
            results.update({sensor_name: MitempSerializer(readlast(sensor_name), many=True).data})
        return JsonResponse(results)

def main_view(request):
    '''Main view'''
    return redirect('temperature_sensor')

#@login_required
def temperature_sensor_view(request):
    '''Temperature sensor view'''
    charts = []
    #if date is sent via form
    if request.method == 'POST':
        StartDate = request.POST['StartDate']                   #retrive vars from forms
        EndDate = request.POST['EndDate']
        try:                                                     #input string verification
            datetime.strptime(StartDate , '%Y-%m-%d')
            datetime.strptime(EndDate, '%Y-%m-%d')
        except ValueError:
            StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
            EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")

        for sensor_name in SENSORS:
            chart = LineChart(StartDate, EndDate, sensor_name)
            charts.append({'sensor_name': sensor_name, 'chart': chart})

        return render(request, 'temperature_sensor/index.html', 
        {
        'charts': charts,
        'StartDate': StartDate,
        'EndDate' : EndDate,
        })


    #no date set
    else:
        StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
        EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")

        for sensor_name in SENSORS:
            chart = LineChart(StartDate, EndDate, sensor_name)
            charts.append({'sensor_name': sensor_name, 'chart': chart})

        return render(request, 'temperature_sensor/index.html', 
        {
        'charts': charts,
        'StartDate': StartDate,
        'EndDate' : EndDate,
        })

#@login_required
def temperature_sensor_view2(request):
    '''Temperature sensor view'''
    charts = []
    #if date is sent via form
    if request.method == 'POST':
        StartDate = request.POST['StartDate']                   #retrive vars from forms
        EndDate = request.POST['EndDate']
        try:                                                     #input string verification
            datetime.strptime(StartDate , '%Y-%m-%d')
            datetime.strptime(EndDate, '%Y-%m-%d')
        except ValueError:
            StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
            EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")

        for sensor_name in SENSORS:
            chart = Chart2(StartDate, EndDate, sensor_name)
            charts.append({
                'sensor_name': sensor_name,
                'datasets': chart.get_datasets(),
                'labels': chart.get_labels(),
            })
        print(charts[0]['labels'])
        return render(request, 'temperature_sensor2/index.html', 
        {
        'charts': charts,
        'StartDate': StartDate,
        'EndDate' : EndDate,
        })

    # no date set
    else:
        StartDate = (datetime.now() - timedelta(1) ).strftime("%Y-%m-%d")
        EndDate = (datetime.now() + timedelta(1) ).strftime("%Y-%m-%d")

        for sensor_name in SENSORS:
            chart = Chart2(StartDate, EndDate, sensor_name)
            charts.append({
                'sensor_name': sensor_name,
                'datasets': chart.get_datasets(),
                'labels': chart.get_labels(),
            })
        print(charts[0])
        return render(request, 'temperature_sensor2/index.html', 
        {
        'charts': charts,
        'StartDate': StartDate,
        'EndDate' : EndDate,
        })

