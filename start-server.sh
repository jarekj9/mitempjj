#!/usr/bin/env bash

if [ -n "admin" ] && [ -n "root1234" ] ; then
    (cd mitempjj; python manage.py createsuperuser --no-input)
fi
(cd mitempjj/temperature_sensor; PYTHONPATH=`pwd`/.. gunicorn temperature_sensor.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) & nginx -g "daemon off;"
