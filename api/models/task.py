from django.db import models
from django.utils.html import mark_safe

import uuid
from api.models import BaseModel, Video, VideoStatus

class TaskAction(models.IntegerChoices):
    START = 0, "Start"
    CANCEL = 1, "Cancel"
    REMOVE = 2, "Remove"
    RESTART = 3, "Restart"


class Task(BaseModel):
    """
    Task run on video
    """
    # ordering = ["-video__timestamp"]
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        serialize=False,
        editable=False,
        help_text="Unique identifier of task within LiveORC database"
    )
    broker_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        serialize=False,
        editable=False,
        help_text="Unique identifier of task as stored by RabbitMQ messaging service"
    )
    pending_action = models.PositiveSmallIntegerField(choices=TaskAction.choices, default=0)
    public = models.BooleanField(default=False)  # very cool to make permalinks publically available when a user wants.
    progress = models.FloatField(
        default=0.,
        help_text="Value between 0 and 1 indicating the progress of the task",
        blank=True
    )
    task_body = models.JSONField(help_text="task body used to perform task by available node.", default=dict)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    status_msg = models.CharField(max_length=5000, help_text="Error messages from back end in case processing failed.")

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        # once the task is saved, take the video instance and update the status
        video = self.video
        if video.status == VideoStatus.NEW:
            video.status = VideoStatus.QUEUE
            video.save()

    def progress_bar(self):
        percentage = round(self.progress * 100)
        return mark_safe("""
<progress value="{perc}" max="100"></progress>
<span style="font-weight:bold">{perc}%</span>""".format(perc=percentage))

    @property
    def institute(self):
        return self.video.institute

