I've made this project to learn and for fun. It has been prepared on raspberry pi 3b+.
It will not work on RPI 1/zero due to architecture.

It works with "Mi Bluetooth Temperature & Humidity Monitor":

![Mi Sensor](misensor.png?raw=true "Mi Sensor")

Project consists of 2 parts:
1. Script poll_sensor.py, which reads data from sensor via bluetooth and writes data to mysql database
2. Docker container, that reads data from mysql and presents interactive graphs in web browser:

![Screenshot](screenshot.jpg?raw=true "Screenshot")


INSTRUCTIONS:



1.Install docker:
```
sudo curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
sudo apt-get install libffi-dev
sudo pip3 install docker-compose
```
2. Download project folder: 
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
7. Running script 'poll_sensor.py' will save sensor data to mysql DB.
This will add it to crontab so it runs every 10 minutes (just replace '/your_path'):
```
(crontab -l 2>/dev/null; echo "*/10 * * * * cd /your_path && python3 /your_path/poll_sensor.py") | crontab - 
```



View data on ```http://<raspberry pi IP>:8083/temperature_sensor```
	
	

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
| |          |           |  | port 8083         | |  |
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


v0.2 18.10.2019
