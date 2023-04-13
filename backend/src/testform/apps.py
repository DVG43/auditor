from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TestFormConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testform'
    verbose_name = _('Testforms')

    def ready(self):
        from testform import signals
