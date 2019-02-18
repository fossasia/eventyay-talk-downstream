# pretalx-docker

This repository contains a docker-compose setup for a complete [pretalx](https://github.com/pretalx/pretalx)
installation.

Includes:

* MySQL as database
* Nginx as webserver 
* Pretalx itself
* Redis for asynchronous tasks
* SMTP sink, for testing purposes

## For testing:

* Run ``./start.sh``  (**only run this once, on the first run!**)
* Open http://localhost/orga in your browser
* Enjoy

You can stop it with:

*  ``docker-compose down``

After initial start, run it in detached mode with:

* ``docker-compose up -d``


## For production

* Change ``conf/pretalx-password.secret``
* Change ``conf/pretalx.conf`` to your [required configuration](https://docs.pretalx.org/en/latest/administrator/configure.html)
   * Set the database password to the same as the previous point;
   * Set the SMTP server
   * Set the correct hostname
* Change ``conf/nginx/conf.d/pretalx.config``
   * Configure hostname
   * **Enable SSL** by adding your certificate and key to ``conf/ssl/cert.pem`` and ``conf/ssl/key.pem``
* You can disable the SMTP from the ``docker-compose.yml`` file (it's just a sink).
* Run ``./start.sh``  (**only run this once, on the first run!**)
* From now on, start up with ``docker-compose up -d`` and stop with ``docker-compose down``

## Using ansible in combination with docker

* add the role under ``ansible-role`` to your ansible setup.
* fill out the varaibles listed in the ``vars/main.yml``-file
* setup an reverse proxy to handle TLS, i recommend traefik. The containers that get rolled out are already tagged for traefik