from django.contrib.gis import admin

class BaseAdmin(admin.GISModelAdmin):
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            # a new object, so change is allowed
            return True
        if request.user == obj.creator:
            return True
        return False
        # return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is not None and request.user == obj.creator:
            return True
        return False
        # return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        model_name = self.model.__name__
        if model_name == "CameraConfig":
            institute = obj.site.institute
        elif model_name == "Video":
            institute = obj.camera_config_obj.site.institute
        else:
            institute = request.user.get_active_institute(request)
        obj.creator = request.user
        obj.institute = institute
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
        return obj.creator == self.request.user
    is_owner.boolean = True
    is_owner.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # super users can see everything. Return all
            return qs
        # Non-super users can only see their own models, and the models from other users within their institute
        qs_filter = qs.filter(institute=request.user.get_active_institute(request))
        return qs_filter


