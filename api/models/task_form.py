from django.db import models
from django.utils import timezone

import uuid
from api.models import BaseModel, Device

class TaskFormStatus(models.IntegerChoices):
    NEW = 0, "New"
    SENT = 1, "Sent"
    ERROR = 2, "Error"
    ACCEPTED = 3, "Accepted"


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
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # we use a uuid to ensure the name is and remain unique and can be used for file naming
    created_on = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text="Date and time on which task form record is created"
    )

    status = models.PositiveSmallIntegerField(choices=TaskFormStatus.choices, default=0)
    task_body = models.JSONField(help_text="task body used to perform task by available node.", default=dict)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    @property
    def institute(self):
        return self.device.institute

