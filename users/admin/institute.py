from django import forms
from django.contrib.gis import admin
from django.contrib import messages
from users.models.institute import Member, TeamRole


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        exclude = (id, )

    def clean(self):
        role = self.cleaned_data.get('role')
        institute = self.cleaned_data.get('institute')
        if Member.objects.filter(institute=institute, role=TeamRole.OWNER).exists() and role == TeamRole.OWNER:
            raise forms.ValidationError("Owner For this Institute Exists. ")
        return self.cleaned_data


class MemberAdmin(admin.GISModelAdmin):
    class Meta:
        model = Member
        # fields = "__all__"
    list_display = ("user", "institute", "role")

    form = MemberForm




