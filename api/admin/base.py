from django import forms
from django.contrib.gis import admin
from api.admin import InstituteFilter

from users.models import Institute

FOREIGN_KEYS = ["institute", "site", "profile", "camera_config"]

class BaseForm(forms.ModelForm):
    class Meta:
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BaseForm, self).__init__(*args, **kwargs)
        # below can be removed when moving to a official app dashboard that relies on the API for back/front comms.
        if not self.request.user.is_superuser:
            # for any foreign keys, it should be checked which of the total available foreign is institutionally owned
            # by user
            for key in FOREIGN_KEYS:
                if key in self.fields:
                        # ensure that only owned institutes are shown
                        choices = []
                        for n, c in enumerate(self.fields[key].choices):
                            if n == 0:
                                # first choice is "leave empty"
                                choices.append(c)
                            elif key == "institute":
                                # institute has owner as direct field
                                if c[0].instance.owner == self.request.user:
                                    choices.append(c)
                            else:
                                # keys other than institute have "institute" as property
                                if c[0].instance.institute.owner == self.request.user:
                                    choices.append(c)
                        self.fields[key].choices = choices

    def clean(self):
        if not self.request.user.is_superuser:
            if len(self.request.user.get_owned_institute_memberships()) == 0:
                # the line below should never occur as you are already not capable of creating or changing if you do not own
                # institutes
                raise forms.ValidationError("You do not own any institutes, please ensure you are owner first.")


class BaseAdmin(admin.GISModelAdmin):

    def has_module_permission(self, request):
        # if user is not staff and does not have any memberships then user is not entitled to anything, so return False
        if request.user.is_superuser:
            return True
        return request.user.is_staff and len(request.user.get_memberships()) > 0

    def has_add_permission(self, request):
        # if user owns any institute, he/she/they is allowed to add new records.
        if request.user.is_superuser:
            return True
        return len(request.user.get_owned_institute_memberships()) > 0
        # return request.user.get_active_membership(request=request).owner == request.user

    def has_view_permission(self, request, obj=None):
        if obj:
            if obj.institute in request.user.get_membership_institutes():
                return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            # a new object, so change is allowed
            return True
        if request.user == obj.institute.owner:
            return True
        return False
        # return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and request.user == obj.institute.owner:
            return True
        return False
        # return super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        admin_form = super(BaseAdmin, self).get_form(request, obj, **kwargs)

        # add the request instance to the Form instance to ensure we have access to the request
        class RequestAdminForm(admin_form):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return admin_form(*args, **kwargs)
        return RequestAdminForm

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()

    list_filter = [InstituteFilter]

    def get_list_display(self, request):
        self.request = request
        fields = super().get_list_display(request)
        if fields is None:
            fields = []
        else:
            fields = list(fields)
        if request.user.is_superuser:
            fields.append("creator")
        fields.append("i_am_owner")
        if len(request.user.get_memberships()) > 1:
            fields.append("institute")
        return fields

    def i_am_owner(self, obj):
        """
        Check if institute belongs to the same user, and if user is also the owner of given institute
        """

        return obj.institute.owner == self.request.user
    i_am_owner.boolean = True
    i_am_owner.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # super users can see everything. Return all
            return qs
        # Non-super users can only see their own models, and the models from other users within their institute
        # A model-specific filter_institute method must be in place for this
        qs_filter = self.filter_institute(request, qs)
        return qs_filter

    def filter_institute(self, request, qs):
        raise ValueError(
            "method `filter_institute` is not, but should be, implemented for this admin view. Please raise an issue "
            "in GitHub."
        )




class BaseInstituteAdmin(BaseAdmin):
    """
    Specific save method in case an institute field is mandatory
    """

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(institute__in=institutes)
