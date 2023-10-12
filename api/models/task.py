from django.contrib.auth import get_user_model
from django.db import models

from ..models import Video

class TaskAction(models.IntegerChoices):
    CANCEL = 1, "Cancel"
    REMOVE = 2, "Remove"
    RESTART = 3, "Restart"


class Task(models.Model):
    """
    Task run on video
    """
    uuid = models.CharField(max_length=255, default='', blank=True,
                            help_text="Identifier of task as stored by RabbitMQ messaging service")
    pending_action = models.PositiveSmallIntegerField(choices=TaskAction.choices)
    asset_paths = models.JSONField(
        default=dict)  # TODO: assets should be filled using task callbacks with new entries such as asset_paths["piv"] = <relative_path_to_piv>
    public = models.BooleanField(default=False)  # very cool to make permalinks publically available when a user wants.
    progress = models.FloatField(default=0., help_text="Value between 0 and 1 indicating the progress of the task",
                                 blank=True)

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

