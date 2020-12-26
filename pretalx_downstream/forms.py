from django import forms
from django.utils.translation import gettext_lazy as _
from hierarkey.forms import HierarkeyForm


class UpstreamSettingsForm(HierarkeyForm):

    downstream_upstream_url = forms.URLField(label=_("Upstream URL"))
    downstream_interval = forms.IntegerField(
        min_value=5, label=_("Interval"), help_text=_("Checking interval in minutes.")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = kwargs.get("obj")
