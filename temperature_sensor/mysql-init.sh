#!/bin/bash
printf "\n[mysqld]\nskip-networking=0\nbind-address=0.0.0.0\n" >> /etc/mysql/mariadb.cnf
service mysql start
mysqladmin -u root create DB
mysql -u root  DB < DB.temperature_sensor-schema.sql
mysql -u root -e "CREATE USER 'pi'@'%' IDENTIFIED BY 's0me_password';"
mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO 'pi'@'%' WITH GRANT OPTION;"
