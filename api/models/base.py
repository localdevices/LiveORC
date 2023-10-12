from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

class BaseModel(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
