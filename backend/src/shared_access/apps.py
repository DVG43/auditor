from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SharedAccessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_access'
    verbose_name = _('Shared access')
    verbose_name_plural = _('Shared access')
