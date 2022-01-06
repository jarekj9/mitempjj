Recent updates:
- 04.01.2022 - v4.0 - Added support for LYWSD03MMC - only with custom firmware, can add multiple sensors
- 31.10.2020 - v3.0 - app is now using nginx+gunicorn, it consumes less cpu
- 30.05.2020 - v2.1 - added simple api to read last values: ```http://<raspberry pi IP>:8083/temperature_sensor/api/```
- 11.11.2019 - v2.0 - changed the app so it uses sqlite and takes less space, old version, using mysql is at : https://github.com/jarekj9/mitempjjv1

**It will not work on RPI 1/zero due to architecture.**
**It probably only works with older sensor - using AAA battery.**
I tested it on RPI 3B+, on fresh raspbian 10 buster install (full).

It works with "Mi Bluetooth Temperature & Humidity Monitor":

![Mi Sensor](misensor.png?raw=true "Mi Sensor")
![LYWSD03MMC](LYWSD03MMC.png?raw=true "LYWSD03MMC")

It can also work with flashed (custom firmware: https://github.com/atc1441/ATC_MiThermometer ) small square sensor LYWSD03MMC.

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

Edit this mac in file:
```mac-address.txt```


6. If you use firewall on rpi, allow connections to rpi on tcp port 8083

Simple example:

```
firewall-cmd --add-port=8083/tcp --permanent
systemctl restart firewalld
#OR:
sudo ufw allow 8083/tcp comment "sensor page"
```
7. Running script 'poll_sensor.py' will save sensor data to sqlite DB.
This will add it to root crontab (root is necessary to read the new square sensor) so it runs every 10 minutes (just replace '/your_path'):
```
(crontab -l 2>/dev/null; echo "*/10 * * * * cd /your_path && python3 /your_path/poll_sensor.py") | sudo crontab - 
```

8. To remove data, delete file: ```database/mitempjj.db``` and to re-create everything:
```
cd mitempjj
docker-compose down
rm database/mitempjj.db
docker-compose up -d --build
```


After some minutes view data on ```http://<raspberry pi IP>:8083/temperature_sensor/```



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
|          |  database/mitepjjj.db   |            |  |
|          |  (sqlite)               |            |  |
|          +-------------+-----------+            |  |
|                        |                        |  |
|                        +------------------------+  |
+----------------------------------------------------+


```
