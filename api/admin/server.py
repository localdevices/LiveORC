from api.admin import BaseAdmin

class ServerAdmin(BaseAdmin):
    list_display = ["type", "url", "end_point", "wildcard", "frequency"]
