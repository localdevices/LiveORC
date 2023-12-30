from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from users.models.institute import Institute


class BaseModel(models.Model):
    """
    This model includes a creator field and an additional property for the institute field
    """
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        editable=False
    )

    class Meta:
        abstract = True

    @property
    def institute(self):
        return self.site.institute


class BaseInstituteModel(models.Model):
    """
    BaseModel with an additional stored field (instead of property) for retrieving the institute
    """
    def __str__(self):
        return "{:s} of {:s}".format(self.name, self.institute.name)

    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        editable=False
    )

    institute = models.ForeignKey(
        Institute,
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
