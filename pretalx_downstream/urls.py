from django.urls import re_path
from pretalx.event.models.event import SLUG_CHARS

from .views import UpstreamSettings

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/upstream/$",
        UpstreamSettings.as_view(),
        name="settings",
    )
]
