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
        # default=get_current_user,
        editable=False
    )

    # institute = models.ForeignKey(Institute, blank=True, null=True, on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
    #     if not(self.pk):
    #         self.user =

    class Meta:
        abstract = True

    @property
    def institute(self):
        return self.site.institute

class BaseInstituteModel(models.Model):
    """
    BaseModel with an additional stored field (instead of property) for retrieving the institute
    """
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        # default=get_current_user,
        editable=False
    )

    institute = models.ForeignKey(Institute, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        abstract = True
