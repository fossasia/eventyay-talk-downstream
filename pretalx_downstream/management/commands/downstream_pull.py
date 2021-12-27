from django.core.management.base import BaseCommand
from django.db import transaction
from django_scopes import scope
from pretalx.event.models import Event

from pretalx_downstream.tasks import task_refresh_upstream_schedule


class Command(BaseCommand):
    help = "Pull an event's upstream data"

    def add_arguments(self, parser):
        parser.add_argument("--event", type=str, help="Slug of the event to be used")
        parser.add_argument("--sync", action="store_true", help="Run synchronously")

    @transaction.atomic
    def handle(self, *args, **options):
        event_slug = options.get("event")
        sync = options.get("sync")

        event = Event.objects.get(slug=event_slug)
        with scope(event=event):
            if sync:
                task_refresh_upstream_schedule(event_slug)
            else:
                task_refresh_upstream_schedule.apply_async(args=(event_slug,))
