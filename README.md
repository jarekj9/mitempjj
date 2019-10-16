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
3. Install python3, docker and docker-compose (https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl)
4. Edit file temperature_sensor/.mitempjj and put your sensor MAC (for example sensor_MAC=4c:65:a8:d4:b9:f0), do not edit other fields
5. Inside main folder run:

```
docker-compose up -d
```

It will create container with www server on django framework and mysql DB.

6. If you use firewall, allow connections to rpi on tcp port 8083

Simple example:

```
firewall-cmd --add-port=8083/tcp --permanent
systemctl restart firewalld
```
7. Running script 'poll_sensor.py' will save sensor data to mysql DB.
This will add it to crontab so it runs every 10 minutes (just replace '/your_path'):

```
(crontab -l 2>/dev/null; echo "*/10 * * * * cd /your_path && python3 /your_path/poll_sensor.py") | crontab - 
```



View data on http://<raspberry pi IP>:8083/temperature_sensor
	
	

Simple Schema:
```
+--------------+              +----------------------+
|              |              |                      |
|  MI SENSOR   |              |  PC with www browser |
|              |              |                      |
+-------+------+              +------------+---------+
        |                                  |
        |                                  |
        |                                  |
        |                                  |
        |                                  |192.168.X.X:8083
+------------------+Raspberry PI+--------------------+
|       |                                  |         |
|       v                +-docker container+------+  |
| +-----+----+           |                 |      |  |
| | polling  |           |  +--------------+----+ |  |
| | script   |           |  | www server(django)| |  |
| |          |           |  |                   | |  |
| +----+-----+           |  |                   | |  |
|      |                 |  +--------------+----+ |  |
|      |                 |                 |      |  |
|      |                 |                 |      |  |
|      |                 |                 |      |  |
|      |                 |            +----v------+  |
|      |      via        |            |          ||  |
|      |      port 13306 |            | MYSQL    ||  |
|      +----------------------------->+ port 3306||  |
|                        |            |          ||  |
|                        |            +-----------|  |
|                        +------------------------|  |
+----------------------------------------------------+



```


v0.2 09.10.2019
