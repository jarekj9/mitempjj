

Install:

1. Copy project folder
2. Install docker and docker-compose
3. Install mariadb(mysql) and create mysql user, that have rights to create databases and tables.
4. Edit project file temperature_sensor/.mitemp and put database details and Mi sensor MAC address (Sensor needs to be connected via bluetooth).
5. Running file 'write_misensor_data.py' will save sensor data to mysql DB. I added this to crontab and it runs every 10 minutes.
5. Inside main folder:
docker-compose up

6. In firewall:
- allow connections from container ip 172.19.0.2 to localhost on mysql tcp port 3306
- allow connections to localhost on tcp port 8083
7. In mysql config allow remote connections.

Check page on http://<raspberry pi IP>:8083/temperature_sensor

Simple Schema:

+--------------+              +----------------------+
|              |              |                      |
|  MI SENSOR   |              |  PC with www browser |
|              |              |                      |
+-------+------+              +-----------+----------+
        |                                 |
        |                                 |
        |                                 |
        |                                 |
        |                                 |
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



