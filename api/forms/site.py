from django import forms
from ..models import Site


class SiteForm(forms.ModelForm):

    class Meta:
        model = Site
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SiteForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.get_active_institute():
            raise forms.ValidationError("You Must have an institute to continue")
