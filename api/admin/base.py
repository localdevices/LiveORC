from django.contrib.gis import admin


class BaseAdmin(admin.GISModelAdmin):
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

    def save_model(self, request, obj, form, change):
        model_name = self.model.__name__
        obj.creator = request.user
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

    def is_owner(self, request, obj):
        model_name = self.model.__name__
        obj_institute = self._get_institute(model_name, obj, request)
        return obj.institue == obj_institute
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
        else:
            qs_filter = qs.filter(institute=request.user.get_active_institute(request))
        return qs_filter

    def _get_institute(self, model_name, obj, request):
        if model_name == "CameraConfig":
            institute = obj.site.institute
        elif model_name == "Video":
            institute = obj.camera_config_obj.site.institute
        else:
            institute = request.user.get_active_institute(request)
        return institute


