from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from django_object_actions import DjangoObjectActions, action
from django.shortcuts import redirect, reverse

from api.models import Video, VideoStatus, Task
from api.task_utils import get_task
from api.admin import BaseAdmin, BaseForm
from api.admin import VideoSiteUserFilter, datetimefilter
from api.tasks import run_nodeorc

class VideoForm(BaseForm):
    class Meta:
        model = Video
        fields = "__all__"

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(VideoForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     if not self.request.user.get_active_membership():
    #         raise forms.ValidationError("You Must have an institute to continue")


class VideoInline(admin.TabularInline):
    """
    Display filtered videos for given site or project inside admin view of site and project
    """
    model = Video
    extra = 3


class VideoAdmin(DjangoObjectActions, BaseAdmin):
    @action(
        label="Queue task",  # optional
        description="Click to queue a task"  # optional
    )
    def toolfunc(self, request, obj):
        # create a new task for this video
        if obj.is_ready_for_task:
            obj.create_task()
        #     # launch creation of a new task
        #     task_body = get_task(obj, request, serialize=False)
        #     # send over validated task to worker
        #     job = run_nodeorc.delayF(obj.pk, task_body)
        #     task = {
        #         "id": task_body["id"],
        #         "broker_id": job.id,
        #         "task_body": task_body,
        #         "video": obj,
        #         "creator": request.user
        #     }
        #     # validation
        #     Task.objects.create(**task)
        #
        #     # once the task is set, change the status of the video
        #     obj.status = VideoStatus.QUEUE
        #     obj.save()
            return redirect('/admin/api/video')
        elif not(obj.time_series):
            messages.error(request, f"Video {obj.id} does not yet have a water level at associated time stamp. ")
        elif obj.status == VideoStatus.QUEUE:
            messages.error(request, f"Video {obj.id} is already in the processing queue. ")
        return HttpResponseRedirect(reverse("admin:api_video_change", args=(obj.pk,)))


    change_actions = ('toolfunc', )

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
        VideoSiteUserFilter,
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
                "status",
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
    form = VideoForm

    def get_readonly_fields(self, request, obj=None):
        # prevent that the file or camera config can be changed afterwards.
        # That is very risky and can lead to inconsistent model records
        if obj:
            return (*self.readonly_fields, "file", "camera_config")
        return self.readonly_fields

    def filter_institute(self, request, qs):
        memberships = request.user.get_memberships()
        institutes = [m.institute for m in memberships]
        return qs.filter(camera_config__site__institute__in=institutes)

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
