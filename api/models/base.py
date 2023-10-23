from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from users.models.institute import Institute


class BaseModel(models.Model):
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        # default=get_current_user,
        editable=False
    )
    institute = models.ForeignKey(Institute, blank=True, null=True, on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
    #     if not(self.pk):
    #         self.user =

    class Meta:
        abstract = True
