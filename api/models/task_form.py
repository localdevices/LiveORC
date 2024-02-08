from django.db import models

import uuid
from api.models import BaseModel, Device

class TaskFormStatus(models.IntegerChoices):
    NEW = 0, "New"
    SENT = 1, "Sent"
    ERROR = 2, "Error"
    ACTIVE = 3, "Active"


class TaskForm(BaseModel):
    """
    Task for run on each video on a node instance
    """
    # ordering = ["-video__timestamp"]
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        serialize=False,
        editable=False,
        help_text="Identifier of task form as stored on both LiveORC and NodeORC side"
    )

    status = models.PositiveSmallIntegerField(choices=TaskFormStatus.choices, default=0)
    task_body = models.JSONField(help_text="task body used to perform task by available node.", default=dict)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    @property
    def institute(self):
        return self.device.institute

