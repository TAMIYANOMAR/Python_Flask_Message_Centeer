#!/bin/sh
docker pull mysql
docker network create python-network
docker run --name mysql_con  --network python-network  -e MYSQL_ROOT_PASSWORD=mysql_pass -d -p 33306:3306 mysql
mysql -u root -p -h localhost -P 33306 -e "CREATE DATABASE kaggle"
mysql -u root -p -h localhost -P 33306 -D kaggle<./sql/make_table.sql
