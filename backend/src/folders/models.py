import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.db.models import ImageField

from common.models import PpmDocModel, permissions
from objectpermissions.registration import register
from utils import get_doc_upload_path


class Folder(PpmDocModel):
    parent_folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='folders',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    doc_order = ArrayField(
        models.UUIDField(null=True), blank=True,
        default=list, verbose_name=_('Frame order'))
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))

    class Meta:
        db_table = "ppm_folders"
        ordering = ['id']
        verbose_name = _('Folder')
        verbose_name_plural = _('Folders')

    def __str__(self):
        return f'FOLDER#{self.id}'


register(Folder, permissions)
