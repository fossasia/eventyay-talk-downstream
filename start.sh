#!/bin/bash
if [ -d "volumes" ]; then
  echo "ERROR: Volumes directory exists! This script has possibly been run before. Bailing out"
  echo "Try running \"docker-compose up -d\" instead"
  exit 0
fi
echo Booting new instance of pretalx...
echo Fetching pretalx
git submodule update --recursive --init
echo Patching docker files
patch -p2 < docker.diff
echo building pretalx docker image
docker-compose build pretalx && \
echo Creating volume folders && \
mkdir -p volumes/mysql-data && \
mkdir -p volumes/nginx-data && \
mkdir -p volumes/pretalx-data && \
mkdir -p volumes/redis-data && \
chown -R 999:999 volumes && \
MYSQL_PASSWORD=`LC_CTYPE=C tr -dc 'a-zA-Z0-9'<  /dev/urandom | fold -w 30 | head -1`
echo Generated mysql root password: $MYSQL_PASSWORD && \
echo $MYSQL_PASSWORD > conf/mysql-password.secret && \
echo Initializing mysql... && \
docker-compose up -d db  && \
echo Waiting 30s to make sure mysql is configured... && \
sleep 30 && \
docker-compose down && \
echo Starting pretalx_core pretalx_celery pretalx_mysql pretalx_nginx pretalx_smtp && \
docker-compose up -d && \
echo Waiting 30s to make sure everything boots up... && \
sleep 30 && \
docker exec -ti pretalx_core pretalx init && \
echo Done.
