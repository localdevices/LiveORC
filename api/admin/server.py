from django import forms
from api.admin import BaseInstituteAdmin, BaseForm
from ..models import Server


class ServerForm(BaseForm):
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(ServerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Server
        fields = "__all__"
    #

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(ServerForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     super().clean()
    #     if not self.request.user.get_active_membership():
    #         raise forms.ValidationError("You Must have an institute to continue")


class ServerAdmin(BaseInstituteAdmin):
    list_display = ["name", "type", "url", "end_point", "wildcard", "frequency"]
    form = ServerForm
