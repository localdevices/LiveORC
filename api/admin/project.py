from django import forms
from api.admin import VideoInline, BaseInstituteAdmin
from api.models import Project
from api.admin import BaseForm


class ProjectForm(BaseForm):
    class Meta:
        model = Project
        fields = "__all__"
    #
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(ProjectForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     super().clean()
    #     if not self.request.user.get_active_membership():
    #         raise forms.ValidationError("You Must have an institute to continue")


class ProjectAdmin(BaseInstituteAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]
    form = ProjectForm
