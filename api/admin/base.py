from django.contrib.gis import admin


class BaseAdmin(admin.GISModelAdmin):

    def has_module_permission(self, request):
        # if user is not staff and does not have any memberships then user is not entitled to anything, so return False
        return request.user.is_staff and len(request.user.get_institutes()) > 0

    def has_add_permission(self, request):
        # if user is owner of the currently active institute, then add permission is granted
        return request.user.get_active_institute(request=request).owner == request.user

    def has_view_permission(self, request, obj=None):
        if obj:
            if obj.institute == request.user.get_active_institute(request=request):
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
        model_name = self.model.__name__
        obj.creator = request.user
        if not request.user.is_superuser:
            obj.institute = self._get_institute(model_name, obj, request)
        obj.save()

    def get_list_display(self, request):
        self.request = request
        fields = super().get_list_display(request)
        if fields is None:
            fields = []
        else:
            fields = list(fields)
        if request.user.is_superuser:
            fields.append("creator")
        fields.append("is_owner")
        return fields

    def is_owner(self, obj):
        """
        Check if institute belongs to the same user, and if user is also the owner of given institute

        Parameters
        ----------
        obj : model instance under consideration

        Returns
        -------
        bool

        """

        # model_name = self.model.__name__
        return obj.institute == self.request.user.get_active_institute(self.request) and obj.institute.owner == self.request.user
        # obj_institute = self._get_institute(model_name, obj, self.request)
        # return obj.institute == obj_institute
    is_owner.boolean = True
    is_owner.allow_tags = True

    def get_queryset(self, request):
        model_name = self.model.__name__
        user_institute = request.user.get_active_institute(request)
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # super users can see everything. Return all
            return qs
        # Non-super users can only see their own models, and the models from other users within their institute
        if model_name == "CameraConfig":
            qs_filter = qs.filter(site__institute=user_institute)
        elif model_name == "Video":
            qs_filter = qs.filter(camera_config_obj__site__institute=user_institute)
        elif model_name == "Task":
            qs_filter = qs.filter(video__camera_config_obj__site__institute=user_institute)
        # elif model_name == "Profile":
        #     qs_filter = qs.filter(video__camera_config_obj__site__institute=user_institute)
        else:
            qs_filter = qs.filter(site__institute=user_institute)
            # qs_filter = qs.filter(institute=request.user.get_active_institute(request))
        return qs_filter

    def _get_institute(self, model_name, obj, request):
        if model_name == "CameraConfig":
            institute = obj.site.institute
        elif model_name == "Video":
            institute = obj.camera_config_obj.site.institute
        else:
            institute = request.user.get_active_institute(request)
        return institute


