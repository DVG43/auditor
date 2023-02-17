import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from objectpermissions.models import UserPermission


class Invite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='invites')
    link = models.UUIDField(default=uuid.uuid4, editable=False)
    permission = models.ForeignKey(
        UserPermission, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        sr = super().save(force_insert=False, force_update=False, using=None,
             update_fields=None)
        print(21, sr)

    class Meta:
        verbose_name = _('Invite')
        verbose_name_plural = _('Invites')
