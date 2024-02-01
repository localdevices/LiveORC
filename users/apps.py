from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'users and institutes'

    # required to ensure a membership is created upon creation of a new institute
    def ready(self):
        import users.signals
