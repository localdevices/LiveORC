from django.db import models
from django_extensions.db.fields import ShortUUIDField


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    slug = ShortUUIDField()

    class Meta:
        abstract = True


def get_object_or_none(model, **kwargs):
    try:
        result = model.objects.get(**kwargs)
    except model.DoesNotExist:
        result = None
    return result



class CustomBaseManager(models.Manager):

    def get_institutional_queryset(self):
        pass