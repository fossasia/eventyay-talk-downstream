#!/bin/bash
cd /pretalx/src
export PRETALX_DATA_DIR=/data
export HOME=/pretalx
export NUM_WORKERS=$((2 * $(nproc --all)))

if [ ! -d /data/logs ]; then
    mkdir /data/logs;
fi
if [ ! -d /data/media ]; then
    mkdir /data/media;
fi

if [ "$1" == "cron" ]; then
    exec python3 -m pretalx runperiodic
fi

python3 -m pretalx migrate --noinput

if [ "$1" == "all" ]; then
    exec sudo /usr/bin/supervisord -n -c /etc/supervisord.conf
fi

if [ "$1" == "webworker" ]; then
    exec gunicorn pretalx.wsgi \
        --name pretalx \
        --workers $NUM_WORKERS \
        --max-requests 1200 \
        --max-requests-jitter 50 \
        --log-level=info \
        --bind=unix:/tmp/pretalx.sock
fi

if [ "$1" == "taskworker" ]; then
    export C_FORCE_ROOT=True
    exec celery -A pretalx.celery_app worker -l info
fi

if [ "$1" == "shell" ]; then
    exec python3 -m pretalx shell
fi

if [ "$1" == "upgrade" ]; then
    exec python3 -m pretalx rebuild
fi

exec python3 -m pretalx $*
