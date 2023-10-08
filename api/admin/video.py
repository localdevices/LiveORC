from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django_object_actions import DjangoObjectActions, action
from django.shortcuts import redirect
from rangefilter.filters import DateRangeFilterBuilder, DateTimeRangeFilterBuilder
from ..models import Video, VideoStatus, Task
from ..task_utils import get_task

from datetime import datetime
from dateutil.relativedelta import relativedelta


default_end = datetime.now()
default_start = default_end - relativedelta(days=1)

datetimefilter = DateTimeRangeFilterBuilder(
    default_start=default_start,
    default_end=default_end
)
class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3

class VideoAdmin(DjangoObjectActions, admin.ModelAdmin):
    @action(
        label="This will be the label of the button",  # optional
        description="This will be the tooltip of the button" # optional
    )
    def toolfunc(self, request, obj):
        # create a new task for this video
        if obj.is_ready_for_task:
            # launch creation of a new task
            task_body = get_task(obj, request, serialize=False)
            task = {
                "id": task_body["id"],
                "task_body": task_body,
                "video": obj
            }
            Task.objects.create(**task)
        # once the task is set, change the status of the video
        obj.status = VideoStatus.QUEUE
        obj.save()
        # TODO: ensure that task and video statusses are updated using AMQP status
        return redirect('/admin/api/video')

    # def queue_task(modeladmin, request, queryset):
    #     queryset.update(status=VideoStatus.QUEUE)
    #
    change_actions = ('toolfunc', )
    # changelist_actions = ('queue_task', )


    ordering = ["-timestamp"]
    list_display = [
        "thumbnail_preview",
        "get_site_name",
        "timestamp",
        "get_water_level",
        "get_fraction",
        "get_discharge",
        "created_at",
        "play_button",
    ]
    non_editable_fields = ["file", "camera_config"]
    readonly_fields = (
        'video_preview',
        'get_site_name',
        'thumbnail_preview',
        'image_preview',
        'get_timestamp',
        'get_water_level',
        'get_discharge',
        'get_fraction',
        'play_button'
    )
    list_filter = [
        "camera_config__site",
        (
            "timestamp",
            datetimefilter,
        ),
        (
            "created_at",
            datetimefilter,
        )
    ]

    fieldsets = [
        ('Video details', {
            "fields": [
                "get_site_name",
                "file",
                "camera_config",
                "timestamp",
                "image_preview",
                "video_preview"
            ]
        }),
        ("Time series instance linked to the video", {
            "fields": [
                "get_timestamp",
                "get_water_level",
                "get_discharge",
                "get_fraction"
            ]}
         )
    ]

    def get_readonly_fields(self, request, obj=None):
        # prevent that the file or camera config can be changed afterwards. That is very risky and can lead to inconsistent
        # model records
        if obj:
            return (*self.readonly_fields, "file", "camera_config")
        return self.readonly_fields


    @admin.display(ordering='camera_config__site__name', description="Site name")
    def get_site_name(self, obj):
        return obj.camera_config.site.name

    @admin.display(ordering='time_series__timestamp', description='Time stamp of related time series')
    def get_timestamp(self, obj):
        return obj.time_series.timestamp

    @admin.display(ordering='time_series__q_50', description='Discharge median [m3/s]')
    def get_discharge(self, obj):
        if obj.time_series:
            if obj.time_series.q_50:
                return round(obj.time_series.q_50, 2)

    @admin.display(ordering='time_series__h', description='Water level [m]')
    def get_water_level(self, obj):
        if obj.time_series:
            if obj.time_series.h:
                return round(obj.time_series.h, 3)

    @admin.display(ordering='time_series__fraction_velocimetry', description='Fraction velocimetry [%]')
    def get_fraction(self, obj):
        if obj.time_series:
            if obj.time_series.fraction_velocimetry:
                return round(obj.time_series.fraction_velocimetry, 1)


    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview
    thumbnail_preview.short_description = 'Thumbnail'
    thumbnail_preview.allow_tags = True

    def video_preview(self, obj):
        return obj.video_preview
    video_preview.short_description = 'video preview'
    video_preview.allow_tags = True

    def image_preview(self, obj):
        return obj.image_preview
    image_preview.short_description = 'Results'
    image_preview.allow_tags = True

    def play_button(self, obj):
        return obj.play_button
    play_button.short_description = "Run/Status"
    play_button.allow_tags = True
