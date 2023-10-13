from django.contrib.gis import admin

class BaseAdmin(admin.GISModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.creator = request.user
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


    #
    #
    # def get_exclude(self, request, obj=None):
    #     fields = super().get_exclude(request)
    #     if not request.user.is_superuser:
    #         if fields is None:
    #             fields = ("creator",)
    #         else:
    #             fields = list(fields)
    #             fields.append("creator")


