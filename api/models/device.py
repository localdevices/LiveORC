from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from api.models import BaseModelNoInstitute


class DeviceStatus(models.IntegerChoices):
    HEALTHY = 0, "Healthy"
    LOW_VOLTAGE = 1, "Low voltage"
    LOW_STORAGE = 2, "Low storage"
    CRITICAL_STORAGE = 3, "Critical storage"


class DeviceFormStatus(models.IntegerChoices):
    NOFORM = 0, "No form"
    VALID_FORM = 1, "Valid form"
    INVALID_FORM = 2, "Invalid form"
    BROKEN_FORM = 3, "Broken form"  # if a valid form used to exist but now is invalid due to system/software changes


class Device(BaseModelNoInstitute):
    """
    Device records, that keep track of field devices, and provide configuration messages to them
    A device belong to a user, not an institute. Based on the configuration, a device can
    also swap for which institute it performs duties.
    """
    id = models.UUIDField(
        primary_key=True,
        help_text="Unique identifier of device"
    )
    name = models.CharField(max_length=250, help_text="Name of device")
    created_at = models.DateTimeField(help_text="Creation date time", default=timezone.now)
    operating_system = models.TextField(help_text="Operating system", null=True)
    processor = models.TextField(help_text="Processor", null=True)
    memory = models.FloatField(help_text="Memory GB", null=True)
    status = models.PositiveSmallIntegerField(choices=DeviceStatus.choices, default=0)
    form_status = models.PositiveSmallIntegerField(choices=DeviceFormStatus.choices, default=0)
    message = models.TextField(help_text="Message from the device, e.g. indicating info on errors", null=True)
    last_seen = models.DateTimeField(help_text="Last seen online", default=timezone.now)
    ip_address = models.GenericIPAddressField(help_text="IP-address of last online occurrence")



    def __str__(self):
        return "Device {:s} at ip address {:s}".format(self.name, self.ip_address)

    def __repr__(self):
        return self.__str__()
