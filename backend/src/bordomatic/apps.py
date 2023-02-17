from django.apps import AppConfig


class BordomaticConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bordomatic'

    def ready(self):
        from . import signals
