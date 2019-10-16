#!/bin/bash
service mysql start
python manage.py runserver 0.0.0.0:8083