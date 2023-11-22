from django import forms
from api.admin import VideoInline, BaseAdmin
from api.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProjectForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        if not self.request.user.get_active_institute():
            raise forms.ValidationError("You Must have an institute to continue")


class ProjectAdmin(BaseAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]
    form = ProjectForm
