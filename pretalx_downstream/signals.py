import datetime as dt

from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_scopes import scope
from pretalx.common.signals import periodic_task
from pretalx.event.models import Event
from pretalx.orga.signals import nav_event_settings

from .tasks import task_refresh_upstream_schedule


@receiver(periodic_task)
def refresh_upstream_schedule(sender, request=None, **kwargs):
    _now = now()
    for event in Event.objects.all():
        with scope(event=event):
            if (
                event.settings.downstream_upstream_url
                and event.datetime_from
                < _now
                < (event.datetime_to + dt.timedelta(days=1))
            ):
                interval = event.settings.downstream_interval or 15
                try:
                    interval = int(interval)
                except TypeError:
                    interval = 5
                interval = dt.timedelta(minutes=interval)
                last_pulled = event.settings.downstream_last_sync
                if not last_pulled or _now - last_pulled > interval:
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
