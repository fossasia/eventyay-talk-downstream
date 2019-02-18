# pretalx-docker

This repository contains a docker-compose setup as well as an ansible rolefor a [pretalx](https://github.com/pretalx/pretalx)
installation based on docker.


## Installation with docker-compose

### For testing
* run ``docker-compose up -d ``, after a few minutes the setup should be accessible under http://localhost/orga
* setup an user and an organizer by running ``docker exec -ti pretalx pretalx init`` 


### For production
* edit ``conf/pretalx.conf`` and fill in your own values
* edit ``docker-compose.yml`` and remove the complete section with ``ports:
 - "80:80"`` from the composefile and chnage the database password.
* if you don't want to use docker volumes create directories for the persistent data and make them read-writeable for the userid 999 and the groupid 999. change ``pretalx-redis, pretalx-db and pretalx-data`` for the correstonding directories you've chosen.
* configure an reverse-proxy to handle TLS. Pretalx listens on port 80 in the ``pretalxdocker``-Network. I recommend to go with traefik for its ease of setup, docker integration and Lets encrypt support (https://docs.traefik.io/user-guide/docker-and-lets-encrypt/)
* run ``docker-compose up -d ``, after a few minutes the setup should be accessible under http://yourdomain.com/orga
* setup an user and an organizer by running ``docker exec -ti pretalx pretalx init`` 


## Installation with ansible

### For testing
* add the role to your ansible setup
* roll out the role
* you should be able to reach pretalx under ``http://localhost/orga``
* setup an user and an organizer by running ``docker exec -ti pretalx pretalx init`` 

### For production
* add the role under ``ansible-role`` to your ansible setup.
* fill out the varaibles listed in the ``vars/main.yml``-file. Make sure to set testing to false!
* setup an reverse proxy to handle TLS, i recommend traefik. The containers that get rolled out are already tagged for traefik
* roll out the role, afterr a few minutes pretalx should be reachable under the configured domain
* setup an user and an organizer by running ``docker exec -ti pretalx pretalx init`` 