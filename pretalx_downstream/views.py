import datetime as dt

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from pretalx.common.mixins.views import PermissionRequired

from .forms import UpstreamSettingsForm
from .tasks import task_refresh_upstream_schedule


class UpstreamSettings(PermissionRequired, FormView):
    form_class = UpstreamSettingsForm
    permission_required = "orga.change_settings"
    template_name = "pretalx_downstream/settings.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        action = request.POST.get("action", "save")
        if action == "refresh":
            try:
                task_refresh_upstream_schedule.apply_async(args=(request.event.slug,))
                messages.success(request, _("Refreshing schedule …"))
            except Exception as e:
                messages.error(
                    request, _("Failure when processing remote schedule: ") + str(e)
                )
        return response

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {
            "obj": self.request.event,
            "attribute_name": "settings",
            **kwargs,
        }

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        last_pulled = self.request.event.settings.upstream_last_sync
        if last_pulled:
            last_pulled = dt.datetime.strptime(last_pulled, "%Y-%m-%dT%H:%M:%S.%f%z")
        return {
            "last_pulled": last_pulled,
            **kwargs,
        }
