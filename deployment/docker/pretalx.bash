#!/bin/bash
cd /pretalx/src
export PRETALX_DATA_DIR=/data
export HOME=/pretalx
export GUNICORN_WORKERS="${GUNICORN_WORKERS:-${WEB_CONCURRENCY:-$((2 * $(nproc --all)))}}"
export GUNICORN_MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-1200}"
export GUNICORN_MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-50}"

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
        --workers "${GUNICORN_WORKERS}" \
        --max-requests "${GUNICORN_MAX_REQUESTS}" \
        --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER}" \
        --log-level=info \
        --bind=0.0.0.0:80
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
