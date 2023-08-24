from django.contrib import admin

class ServerAdmin(admin.ModelAdmin):
    list_display = ["type", "url", "end_point", "wildcard", "frequency"]
