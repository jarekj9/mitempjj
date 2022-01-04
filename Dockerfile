# Django
# Version: 4.0
FROM python:3-slim

# add user pi to chown/share database volume
RUN groupadd -r -g 1000 pi && useradd -r -g pi -u 1000 pi

# install nginx
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get update && apt-get install nginx -y --no-install-recommends
RUN apt-get install -y \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    vim

COPY nginx/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/mitempjj
COPY mitempjj/requirements.txt start-server.sh /opt/app/
COPY mitempjj /opt/app/mitempjj/
WORKDIR /opt/app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --cache-dir /opt/app/pip_cache
RUN chown -R www-data:www-data /opt/app
RUN mkdir -p /opt/app/mitempjj/database
RUN chown -R pi:pi /opt/app/mitempjj/database

# Server
STOPSIGNAL SIGINT
ENTRYPOINT ["sh"]
CMD ["/opt/app/start-server.sh"]
