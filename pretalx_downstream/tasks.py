from pretalx.celery_app import app
from pretalx.event.models import Event


@app.task()
def task_refresh_upstream_schedule(event_slug):
    pass
