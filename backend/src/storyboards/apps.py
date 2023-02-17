from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StoryboardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'storyboards'
    verbose_name = _('Storyboards')
