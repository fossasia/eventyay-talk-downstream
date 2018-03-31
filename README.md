# pretalx-docker
docker setup for a complete [pretalx](https://github.com/pretalx/pretalx) instalation using docker

Includes:

* Mysql database
* nginx 
* Pretalx
* Redis server for pretalx celery
* SMTP sink, for testing purposes

Requires docker-compose

## For testing:

* run ./start.sh  (**only run this once, on the first run!!!**)
* Open http://localhost/orga in the browser
* enjoy

You can stop it with:

*  docker-compose down

After initial start, run it with:

* docker-compose up -d


## For production

* Change conf/pretalx-password.secret;
* Change conf/pretalx.conf to your required configuration.
 * Set the database password to the same as the previous point; 
 * Set the SMTP server
 * Set the correct hostname
 
* Change conf/nginx/conf.d/pretalx.config 
 * Configure hostname
 * **Enable SSL**

* Add your certificate and key to conf/ssl/cert.pem and conf/ssl/key.pem

You can disable the SMTP from the docker-compose.yml file (it's just a sink)

Run ./start.sh  (**only run this once, on the first run!!!**)

 
You can stop it with:

*  docker-compose down

After initial start, run it with:

* docker-compose up -d

