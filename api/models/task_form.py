from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe

import uuid
from api.models import BaseModelNoInstitute, BaseInstituteModel, Device

class TaskFormStatus(models.IntegerChoices):
    NEW = 0, "New"
    SENT = 1, "Sent"
    ERROR = 2, "Error"
    ACCEPTED = 3, "Accepted"


class TaskForm(BaseInstituteModel):
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

    def __str__(self):
        return "Task {:s} for {:s}".format(str(self.id), str(self.device))

    @property
    def status_icon(self):
        if self.status == TaskFormStatus.NEW:
            return mark_safe('<i class="fa-solid fa-spinner"></i> New')

        elif self.status == TaskFormStatus.SENT:
            return mark_safe(
                f"""<i class="fa-solid fa-stopwatch" style="color: #417893;"></i> Sent"""
            )
        elif self.status == TaskFormStatus.ERROR:
            return mark_safe(
                f"""<img src="/static/admin/img/icon-no.svg" alt="True"> Error"""
            )
        else:
            # accepted
            return mark_safe(
                f"""<img src="/static/admin/img/icon-yes.svg" alt="True"> Done"""
            )
