from django.forms import CharField, ChoiceField, IntegerField, RadioSelect, URLField
from django.utils.translation import gettext_lazy as _
from hierarkey.forms import HierarkeyForm


class UpstreamSettingsForm(HierarkeyForm):
    downstream_upstream_url = URLField(
        label=_("Upstream URL"),
        help_text=_("URL of your schedule.xml"),
        required=True,
    )
    downstream_interval = IntegerField(
        min_value=5, label=_("Interval"), help_text=_("Checking interval in minutes.")
    )
    downstream_checking_time = ChoiceField(
        choices=(
            ("event", _("Check only during event time")),
            ("always", _("From now until one day after the event ends")),
        ),
        label=_("Schedule check time"),
        widget=RadioSelect,
    )
    downstream_discard_after = CharField(
        label=_("Discard version name after"),
        help_text=_(
            "Everything after the first occurence of the entered string "
            "in schedule version will be discarded. Leave empty if you "
            "want to keep the full schedule version"
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = kwargs.get("obj")
