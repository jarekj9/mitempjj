# Django
# Version: 1.0
FROM python:3-slim
# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    net-tools \
    vim
# Project Files and Settings
ARG PROJECT=django
ARG PROJECT_DIR=/var/www/${PROJECT}
RUN mkdir -p $PROJECT_DIR

RUN mkdir -p $PROJECT_DIR/temperature_sensor
COPY temperature_sensor $PROJECT_DIR/temperature_sensor
WORKDIR $PROJECT_DIR/temperature_sensor


COPY requirements.txt .
RUN pip install -r requirements.txt
# Server
EXPOSE 8083
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8083"]
