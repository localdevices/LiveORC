from django.contrib import admin

class TaskAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
