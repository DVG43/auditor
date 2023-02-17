from django.apps import AppConfig


class TimingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timing'

    def ready(self):
        from . import signals
