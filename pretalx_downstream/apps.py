from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from pretalx_downstream import __version__


class PluginApp(AppConfig):
    name = "pretalx_downstream"
    verbose_name = "eventyay-talk as a downstream service"

    class PretalxPluginMeta:
        name = gettext_lazy("pretalx as a downstream service")
        author = "Tobias Kunze"
        description = gettext_lazy(
            "This plugin allows you to use eventyay-talk passively, by letting it import another event's schedule."
        )
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # NOQA
