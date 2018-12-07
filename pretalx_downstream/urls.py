from django.conf.urls import url
from pretalx.event.models.event import SLUG_CHARS

from .views import UpstreamSettings

urlpatterns = [
    url(fr'^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/upstream/$', UpstreamSettings.as_view(), name='settings')
]
