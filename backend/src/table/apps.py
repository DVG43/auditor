from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DefaultTablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'table'
    verbose_name = _('Table')
