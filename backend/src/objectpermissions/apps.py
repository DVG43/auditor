from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommmonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'objectpermissions'
    verbose_name = _('Object permissions')
