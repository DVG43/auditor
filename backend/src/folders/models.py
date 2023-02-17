from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import PpmDocModel, permissions
from objectpermissions.registration import register


class Folder(PpmDocModel):
    host_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='folders',
        verbose_name=_('Project'))
    parent_folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='folders',
        verbose_name=_('Folder'),
        blank=True, null=True
    )

    class Meta:
        db_table = "ppm_folders"
        ordering = ['id']
        verbose_name = _('Folder')
        verbose_name_plural = _('Folders')

    def __str__(self):
        return f'FOLDER#{self.id}'


register(Folder, permissions)
