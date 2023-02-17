from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShootingplansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shootingplans'
    verbose_name = _('Shootingplans')
