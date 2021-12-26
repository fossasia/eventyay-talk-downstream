import datetime as dt

from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_scopes import scope
from pretalx.common.models.settings import hierarkey
from pretalx.common.signals import periodic_task
from pretalx.event.models import Event
from pretalx.orga.signals import nav_event_settings

from .tasks import task_refresh_upstream_schedule

hierarkey.add_default("downstream_interval", 15)
hierarkey.add_default("downstream_checking_time", "event")


@receiver(periodic_task)
def refresh_upstream_schedule(sender, request=None, **kwargs):
    _now = now()
    for event in Event.objects.all():
        with scope(event=event):
            if not event.settings.downstream_upstream_url:
                continue

            if not _now < (event.datetime_to + dt.timedelta(days=1)):
                continue

            if not (
                event.settings.downstream_checking_time == "always"
                or event.datetime_from < _now
            ):
                continue

            try:
                interval = int(event.settings.downstream_interval)
            except TypeError:
                interval = 5

            interval = dt.timedelta(minutes=interval)
            last_pulled = event.settings.upstream_last_sync

            if (
                not last_pulled
                or _now - dt.datetime.strptime(last_pulled, "%Y-%m-%dT%H:%M:%S.%f%z")
                > interval
            ):
                task_refresh_upstream_schedule.apply_async(
                    kwargs={"event_slug": event.slug}
                )

            if event.upstream_results.count() > 3:
                latest_three = list(event.upstream_results.order_by("-timestamp")[:3])
                event.upstream_results.filter(
                    timestamp__lt=latest_three[-1].timestamp
                ).delete()


@receiver(nav_event_settings)
def register_upstream_settings(sender, request, **kwargs):
    if not request.user.has_perm("orga.change_settings", request.event):
        return []
    return [
        {
            "label": _("Upstream"),
            "url": reverse(
                "plugins:pretalx_downstream:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_downstream:settings",
        }
    ]
