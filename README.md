# pretalx-docker

This repository contains a docker-compose setup as well as an [ansible](https://docs.ansible.com) role for a
[pretalx](https://github.com/pretalx/pretalx) installation based on docker.

**Please note that this repository is provided by the pretalx community, and not supported by the pretalx team.**

## Installation with docker-compose

### For testing

* Run ``docker-compose up -d``. After a few minutes the setup should be accessible at http://localhost/orga
* Set up a user and an organizer by running ``docker exec -ti pretalx pretalx init``.

### For production

* Edit ``conf/pretalx.cfg`` and fill in your own values (→ [configuration
  documentation](https://docs.pretalx.org/en/latest/administrator/configure.html))
* Edit ``docker-compose.yml`` and remove the complete section with ``ports: - "80:80"`` from the file (if you go with
  traefic as reverse proxy) or change the line to ``ports: - "127.0.0.1:8355:80"`` (if you use nginx). **Change the
  database password.**
* If you don't want to use docker volumes, create directories for the persistent data and make them read-writeable for
  the userid 999 and the groupid 999. Change ``pretalx-redis``, ``pretalx-db``, ``pretalx-data`` and ``pretalx-public`` to the corresponding
  directories you've chosen.
* Configure a reverse-proxy for better security and to handle TLS. Pretalx listens on port 80 in the ``pretalxdocker``
  network. I recommend to go with traefik for its ease of setup, docker integration and [LetsEncrypt
  support](https://docs.traefik.io/user-guide/docker-and-lets-encrypt/). An example to copy into the normal compose file
  is located at ``reverse-proxy-examples/docker-compose``. You can also find a few words on an nginx configuration at
  ``reverse-proxy-examples/nginx``
* Optional: To adjust the number of [Gunicorn workers](https://docs.gunicorn.org/en/stable/settings.html#workers), provide
  the container with `GUNICORN_WORKERS` environment variable. Similarly you can use `GUNICORN_MAX_REQUESTS` and
  `GUNICORN_MAX_REQUESTS_JITTER` to configure the requests a worker instance will process before restarting. `GUNICORN_FORWARDED_ALLOW_IPS` lets you specify which IPs to trust (i.e. which reverse proxies' `X-Forwarded-*` headers can be used to infer connection security).
  Here's how to set an environment variable [in
  `docker-compose.yml`](https://docs.docker.com/compose/environment-variables/set-environment-variables/)
  or when using [`docker run` command](https://docs.docker.com/engine/reference/run/#env-environment-variables).
* Run ``docker-compose up -d ``. After a few minutes the setup should be accessible under http://yourdomain.com/orga
* Set up a user and an organizer by running ``docker exec -ti pretalx pretalx init``.
* Set up a cronjob for periodic tasks like this ``15,45 * * * * docker exec pretalx-app pretalx runperiodic``


## Installation with ansible

(Please note that we also provide a second ansible role for use without docker
[here](https://github.com/pretalx/ansible-pretalx/)).

### For testing

* Add the role at ``ansible-role`` to your ansible setup.
* Roll out the role
* You should be able to reach pretalx at ``http://localhost/orga``
* Set up a user and an organizer by running ``docker exec -ti pretalx pretalx init``.

### For production

* Add the role at ``ansible-role`` to your ansible setup.
* Fill in the variables listed in the ``vars/main.yml`` file. **Make sure to set testing to false!**
* Set up a reverse proxy to handle TLS. traefik is recommended. The containers that get rolled out are already tagged
  for traefik. An example role for traefik is included at ``reverse-proxy-examples/ansible/traefik``.
* Roll out the role. After a few minutes pretalx should be reachable at the configured domain.
* Set up a user and an organizer by running ``docker exec -ti pretalx pretalx init`` .
