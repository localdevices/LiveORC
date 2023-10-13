from api.admin import VideoInline, BaseAdmin


class ProjectAdmin(BaseAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]
