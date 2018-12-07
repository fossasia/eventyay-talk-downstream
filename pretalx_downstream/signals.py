from datetime import timedelta

from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from pretalx.common.signals import periodic_task
from pretalx.orga.signals import nav_event_settings

from .tasks import task_refresh_upstream_schedule


@receiver(periodic_task)
def refresh_upstream_schedule(sender, request, **kwargs):
    interval = timedelta(minutes=sender.settings.downstream_interval or 5)
    last_pulled = sender.settings.downstream_last_sync
    if not last_pulled or now() - last_pulled > interval:
        task_refresh_upstream_schedule.apply_async(sender.slug)


@receiver(nav_event_settings)
def register_upstream_settings(sender, request, **kwargs):
    if not request.user.has_perm('orga.change_settings', request.event):
        return []
    return [
        {
            'label': _('Upstream'),
            'url': reverse(
                'plugins:pretalx_downstream:settings',
                kwargs={'event': request.event.slug},
            ),
            'active': request.resolver_match.url_name
            == 'plugins:pretalx_downstream:settings',
        }
    ]
