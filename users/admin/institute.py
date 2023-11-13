from django import forms
from django.contrib.gis import admin
from django.contrib import messages
from LiveORC.utils import choices
from ..models.institute import Member


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        exclude = (id, )

    def clean(self):
        role = self.cleaned_data.get('role')
        institute = self.cleaned_data.get('institute')
        if Member.objects.filter(institute=institute, role=choices.TeamRole.OWNER).exists() and role == choices.TeamRole.OWNER:
            raise forms.ValidationError("Owner For this Institute Exists. ")
        return self.cleaned_data


class MemberAdmin(admin.GISModelAdmin):

    form = MemberForm




