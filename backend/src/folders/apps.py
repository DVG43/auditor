from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FoldersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'folders'
    verbose_name = _('Folders')
