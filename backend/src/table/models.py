from common.models import PpmDocModel, permissions
from django.db import models
from django.utils.translation import gettext_lazy as _

from document.models import Document
from folders.models import Folder
from objectpermissions.registration import register


class DefaultTableModel(PpmDocModel):
    host_document = models.ForeignKey(Document, related_name="tables", on_delete=models.CASCADE,
                                      null=True, blank=True)
    host_folder = models.ForeignKey(Folder, related_name="tables", on_delete=models.CASCADE,
                                    null=True, blank=True)

    frame_columns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_default_table',
        verbose_name=_('Frame columns')
    )

    class Meta:
        db_table = "default_table"
        ordering = ['id']
        verbose_name = _('Table')
        verbose_name_plural = _('Tables')

    def __str__(self):
        return f'Default table#{self.id}'


class DefaultTableFrame(PpmDocModel):
    host_default_table = models.ForeignKey(
        DefaultTableModel,
        on_delete=models.CASCADE,
        related_name='table_frames',
        verbose_name=_('Table'))
    userfields = models.ManyToManyField(
        'common.UserCell',
        related_name='of_table_frame',
        blank=True)

    class Meta:
        db_table = "table_frames"
        ordering = ['id']
        verbose_name = _('Tableframe')
        verbose_name_plural = _('Tableframes')

    def __str__(self):
        return f'Table frame#{self.id}'


register(DefaultTableModel, permissions)
register(DefaultTableFrame, permissions)
