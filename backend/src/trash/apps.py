from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TrashConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trash'
    verbose_name = _('Recycle bin')
