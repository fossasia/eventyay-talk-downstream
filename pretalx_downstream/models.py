import hashlib

from django.db import models
from django_scopes import ScopedManager


class UpstreamResult(models.Model):
    event = models.ForeignKey(
        to="event.Event", on_delete=models.CASCADE, related_name="upstream_results"
    )
    schedule = models.ForeignKey(
        to="schedule.Schedule",
        null=True,
        on_delete=models.CASCADE,
        related_name="upstream_results",
    )
    content = models.TextField(null=True, blank=True)
    changes = models.TextField(
        null=True, blank=True
    )  # contains only content changes, all regular changes will be showin in the related schedule update (if any)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ScopedManager(event="event")

    @property
    def checksum(self):
        if not self.content:
            return None
        m = hashlib.sha256()
        m.update(self.content.encode("utf-8"))
        return m.hexdigest()
