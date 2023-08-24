from django.contrib import admin
from ..admin import VideoInline

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    inlines = [VideoInline]
