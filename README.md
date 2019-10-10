It works with "Mi Bluetooth Temperature & Humidity Monitor":

![Mi Sensor](misensor.png?raw=true "Mi Sensor")

Project consists of 2 parts:
1. Script poll_sensor.py, which reads data from sensor via bluetooth and writes data to mysql database
2. Docker container, that reads data from mysql and presents interactive graphs in web browser:

![Screenshot](screenshot.jpg?raw=true "Screenshot")


1. Download project folder
2. Install docker and docker-compose
3. Install mariadb(mysql) and create mysql user, that have rights to create databases and tables.
4. Create file temperature_sensor/.mitempjj -> put database details and Mi sensor MAC address (Sensor needs to be connected via bluetooth):

cat temperature_sensor/.mitempjj
db_address=localhost
db_name=DB
db_login=your_login
db_password=your_password
sensor_MAC=4c:65:a8:d4:b9:f0

5. Running script 'poll_sensor.py' will save sensor data to mysql DB. I added this to crontab and it runs every 10 minutes.
6. Inside main folder run:

docker-compose up

It will create container with www server on django framework.
It will copy temperature_sensor/.mitempjj inside container during creation (important for DB login/password)
Container ip: 172.19.0.2
WWW server port: 8083

6. If you use firewall:
- allow connections from container ip 172.19.0.2 to localhost on mysql tcp port 3306
- allow connections to localhost on tcp port 8083

7. In mysql config allow remote connections:
/etc/mysql/mariadb.cnf:
...
[mysqld]
skip-networking=0
...

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


v0.1 09.10.2019
