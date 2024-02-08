from django.db import models
from django.utils import timezone
from datetime import datetime

from api.models import BaseInstituteModel


class Device(BaseInstituteModel):
    """
    Device records, that keep track of field devices, and provide configuration messages to them
    """
    id = models.UUIDField(
        primary_key=True,
        # editable=False,
        help_text="Unique identifier of device"
    )
    name = models.CharField(max_length=250, help_text="Name of device")
    created_on = models.DateTimeField(help_text="Creation date time", default=timezone.now)
    operating_system = models.TextField(help_text="Operating system", null=True)
    processor = models.TextField(help_text="Processor", null=True)
    memory = models.FloatField(help_text="Memory GB", null=True)
    last_seen = models.DateTimeField(help_text="Last seen online", default=timezone.now)
    ip_address = models.GenericIPAddressField(help_text="IP-address of last online occurrence")

