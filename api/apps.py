from django.apps import AppConfig
from api import __version__


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Assets'
    version = __version__
    def ready(self):
        print(f"LiveORC version {self.version} {self.verbose_name} loaded")
