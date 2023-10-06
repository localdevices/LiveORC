from django.db import models
import uuid
from ..models import Video

class TaskAction(models.IntegerChoices):
    START = 0, "Start"
    CANCEL = 1, "Cancel"
    REMOVE = 2, "Remove"
    RESTART = 3, "Restart"


class Task(models.Model):
    """
    Task run on video
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        serialize=False,
        editable=False,
        help_text="Identifier of task as stored by RabbitMQ messaging service"
    )
    pending_action = models.PositiveSmallIntegerField(choices=TaskAction.choices, default=0)
    public = models.BooleanField(default=False)  # very cool to make permalinks publically available when a user wants.
    progress = models.FloatField(default=0., help_text="Value between 0 and 1 indicating the progress of the task",
                                 blank=True)
    task_body = models.JSONField(help_text="task body used to perform task by available node.", default=dict)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)


