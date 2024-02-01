from django import forms
from api.admin import VideoInline, BaseInstituteAdmin
from api.models import Project
from api.admin import BaseForm


class ProjectForm(BaseForm):
    class Meta:
        model = Project
        fields = "__all__"


class ProjectAdmin(BaseInstituteAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]
    form = ProjectForm
