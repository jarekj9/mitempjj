I've made this project to learn and for fun. It has been prepared on raspberry pi 3b+.
It works with "Mi Bluetooth Temperature & Humidity Monitor":

![Mi Sensor](misensor.png?raw=true "Mi Sensor")

Project consists of 2 parts:
1. Script poll_sensor.py, which reads data from sensor via bluetooth and writes data to mysql database
2. Docker container, that reads data from mysql and presents interactive graphs in web browser:

![Screenshot](screenshot.jpg?raw=true "Screenshot")


INSTRUCTIONS:

1. Connect your sensor via bluetooth, see for example : https://zsiti.eu/xiaomi-mijia-hygrothermo-v2-sensor-data-on-raspberry-pi/
2. Download project folder
3. Install docker and docker-compose
4. Install mariadb(mysql) and create mysql user, that have rights to create databases and tables.
5. Create file temperature_sensor/.mitempjj -> put database details and Mi sensor MAC address (Sensor needs to be connected via bluetooth):

```
cat temperature_sensor/.mitempjj
db_address=localhost
db_name=DB
db_login=your_login
db_password=your_password
sensor_MAC=4c:65:a8:d4:b9:f0
```

6. Running script 'poll_sensor.py' will save sensor data to mysql DB. I added this to crontab and it runs every 10 minutes.
7. Inside main folder run:

docker-compose up

It will create container with www server on django framework.
It will copy temperature_sensor/.mitempjj inside container during creation (important for DB login/password)

Container ip: 172.19.0.2
WWW server port: 8083

8. If you use firewall:
- allow connections from container ip 172.19.0.2 to rpi on mysql tcp port 3306
- allow connections to rpi on tcp port 8083

Simple example:

```
firewall-cmd --add-port=8083/tcp --permanent
firewall-cmd --add-port=3306/tcp --permanent
systemctl restart firewalld
```
9. In mysql config allow remote connections:

```
/etc/mysql/mariadb.cnf:
...
[mysqld]
skip-networking=0
...
```

View data on http://<raspberry pi IP>:8083/temperature_sensor

Simple Schema:
```
+--------------+              +----------------------+
|              |              |                      |
|  MI SENSOR   |              |  PC with www browser |
|              |              |                      |
+-------+------+              +-----------+----------+
        |                                 |
        |                                 |
        |                                 |
        |                                 |
        |                                 | 192.168.X.X:8083
+------------------+Raspberry PI+--------------------+
|       |                                 |          |
|       v                      +----------v-------+  |
| +-----+----+                 |Dockerized WWW    |  |
| | Polling  |                 |server            |  |
| | script   |                 |                  |  |
| |          |                 | copy config      |  |
| +-----+----+                 | during creation  |  |
|       |                      |                  |  |
|       |                      |                  |  |
|       |                      |                  |  |
|       v                      |                  |  |
|                              |                  |  |
| +----------+                 |                  |  |
| |          |                 | Hardcode IPs:    |  |
| | MYSQL    | <---------------+ 172.19.0.2       |  |
| |          |docker:          |                  |  |
| |          |172.19.0.1       |                  |  |
| +----------+                 +------------------+  |
+----------------------------------------------------+
```

TO DO:

-simplify installation

v0.1 09.10.2019
