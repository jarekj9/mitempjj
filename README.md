I updated this project on 11.11.2019 so it uses sqlite and takes less space.
Old version, using mysql is at : https://github.com/jarekj9/mitempjjv1

It will not work on RPI 1/zero due to architecture.
I tested it on RPI 3B+, on fresh raspbian 10 buster install (full).

It works with "Mi Bluetooth Temperature & Humidity Monitor":

![Mi Sensor](misensor.png?raw=true "Mi Sensor")

Project consists of 2 parts:
1. Script poll_sensor.py, which reads data from sensor via bluetooth and writes data to sqlite database
2. Docker container, that reads data from sqlite and presents interactive graphs in web browser:

![Screenshot](screenshot.jpg?raw=true "Screenshot")


INSTRUCTIONS:



1.Install docker:
```
sudo curl -sSL https://get.docker.com | sh
sudo apt-get install libffi-dev
sudo pip3 install docker-compose
sudo usermod -aG docker pi
logout
```

2. Re-login to rpi and download project folder: 
```
git clone https://github.com/jarekj9/mitempjj.git
cd mitempjj
```
3. Create image and run container:
```
docker-compose up -d
```
Check with command 'docker ps' if container is running.

4. Install additional python3 packages:
```
sudo pip3 install -r requirements.txt
```
5. Check xiaomi sensor MAC address and add it to file:
```
sudo blescan
```
(The MAC should have description like: Complete Local Name: 'MJ_HT_V1'

Edit this mac in file (just MAC, don't edit other fieds):
```temperature_sensor/.mitempjj```


6. If you use firewall, allow connections to rpi on tcp port 8083

Simple example:

```
firewall-cmd --add-port=8083/tcp --permanent
systemctl restart firewalld
```
7. Running script 'poll_sensor.py' will save sensor data to sqlite DB.
This will add it to crontab so it runs every 10 minutes (just replace '/your_path'):
```
(crontab -l 2>/dev/null; echo "*/10 * * * * cd /your_path && python3 /your_path/poll_sensor.py") | crontab - 
```



View data on ```http://<raspberry pi IP>:8083/temperature_sensor/```


Check if container is running:
```
$ docker ps -a
CONTAINER ID        IMAGE                        COMMAND               CREATED             STATUS                   PORTS                    NAMES
6300d0b0fbc7        django_temperature_sensor2   "sh entry-point.sh"   22 hours ago        Up 22 hours              0.0.0.0:8083->8083/tcp   django_temperature_sensor2
```
To remove container:
```
Stop and remove container:
$docker stop 6300d0b0fbc7
$docker remove 6300d0b0fbc7
```
To remove image:
```
$ docker image ls
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
django_temperature_sensor2   latest              89b8c59f3638        22 hours ago        335MB

$docker image rm django_temperature_sensor2
```
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
|       v                ++docker container+------+  |
| +-----+----+           |                 |      |  |
| | polling  |           |  +--------------+----+ |  |
| | script   |           |  | www server(django)| |  |
| |          |           |  | port 8083         | |  |
| +---------++           |  |                   | |  |
|           |            |  +-----+-------------+ |  |
|           |            |        |               |  |
|           |            |        |               |  |
|           v            |        v               |  |
|          ++------------+--------+--+            |  |
|          |  shared volume:         |            |  |
|          |  /database/mitepjjj.db  |            |  |
|          |  (sqlite)               |            |  |
|          +-------------+-----------+            |  |
|                        |                        |  |
|                        +------------------------+  |
+----------------------------------------------------+


```


v2 11.11.2019
