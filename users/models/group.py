from django.contrib.auth.models import Group as DjangoGroup

class Group(DjangoGroup):
    class Meta:
        app_label = 'users'

