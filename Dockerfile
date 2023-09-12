FROM python:3.10-bookworm

RUN apt-get update && \
    apt-get install -y git gettext libmariadb-dev libpq-dev locales libmemcached-dev build-essential \
            supervisor \
            sudo \
            locales \
            --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8 && \
    mkdir /etc/pretalx && \
    mkdir /data && \
    groupadd -g 999 pretalxuser && \
    useradd -r -u 999 -g pretalxuser -d /pretalx -ms /bin/bash pretalxuser && \
    echo 'pretalxuser ALL=(ALL) NOPASSWD: /usr/bin/supervisord' >> /etc/sudoers

ENV LC_ALL=C.UTF-8


COPY pretalx/pyproject.toml /pretalx
COPY pretalx/src /pretalx/src
COPY deployment/docker/pretalx.bash /usr/local/bin/pretalx
COPY deployment/docker/supervisord.conf /etc/supervisord.conf

RUN pip3 install -U pip setuptools wheel typing && \
    pip3 install -e /pretalx/ && \
    pip3 install django-redis pylibmc mysqlclient psycopg2-binary redis==3.3.1 && \
    pip3 install gunicorn


RUN python3 -m pretalx makemigrations
RUN python3 -m pretalx migrate

RUN apt-get update && \
    apt-get install -y nodejs npm && \
    python3 -m pretalx rebuild && \
    apt-get remove -y nodejs npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN chmod +x /usr/local/bin/pretalx && \
    cd /pretalx/src && \
    rm -f pretalx.cfg && \
    chown -R pretalxuser:pretalxuser /pretalx /data && \
    rm -f /pretalx/src/data/.secret

USER pretalxuser
VOLUME ["/etc/pretalx", "/data"]
EXPOSE 80
ENTRYPOINT ["pretalx"]
CMD ["all"]
