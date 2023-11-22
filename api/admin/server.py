from django import forms
from api.admin import BaseAdmin
from ..models import Server


class ServerForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ServerForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.request.user.get_active_institute():
            raise forms.ValidationError("You Must have an institute to continue")


class ServerAdmin(BaseAdmin):
    list_display = ["type", "url", "end_point", "wildcard", "frequency"]
    form = ServerForm
