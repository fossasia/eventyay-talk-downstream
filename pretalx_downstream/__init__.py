from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class PluginApp(AppConfig):
    name = 'pretalx_downstream'
    verbose_name = 'pretalx as a downstream service'

    class PretalxPluginMeta:
        name = ugettext_lazy('pretalx as a downstream service')
        author = 'Tobias Kunze'
        description = ugettext_lazy('This plugin allows you to use pretalx passively, by letting it import another event\'s schedule.')
        visible = True
        version = '0.0.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretalx_downstream.PluginApp'
