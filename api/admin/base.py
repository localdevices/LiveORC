from django.contrib.gis import admin

class BaseAdmin(admin.GISModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
