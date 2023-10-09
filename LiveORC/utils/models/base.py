from django.db import models


class CustomBaseManager(models.Manager):

    def get_institutional_queryset(self):
        pass

