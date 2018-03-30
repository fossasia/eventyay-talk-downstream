#!/bin/bash
cd /src
exec celery -A pretalx.celery_app worker -l info
