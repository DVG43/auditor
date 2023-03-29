from django.db import models
from django.utils.translation import gettext_lazy as _


class Portal(models.Model):
    """
    Portal
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(_('Title'), max_length=255)
    domain = models.CharField(_('Domain'), max_length=64, unique=True)
    default = models.BooleanField(_('Default'), default=False)
    description = models.TextField(
        _('Description'),
        blank=True,
        max_length=1000
    )
    owner = models.ForeignKey(
        'accounts.User',
        verbose_name=_('Owner'),
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)
