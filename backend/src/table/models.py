import uuid

from django.contrib.postgres.fields import ArrayField

from accounts.models import ResizeImageMixin
from common.models import PpmDocModel, permissions, UserCell, UserColumn, UserChoice
from django.db import models
from django.utils.translation import gettext_lazy as _

from document.models import Document
from folders.models import Folder
from objectpermissions.registration import register
from utils import get_doc_upload_path


class DefaultTableModel(PpmDocModel):
    host_document = models.ForeignKey(Document, related_name="tables", on_delete=models.CASCADE,
                                      null=True, blank=True)
    folder = models.ForeignKey(Folder, related_name="tables", on_delete=models.CASCADE,
                                    null=True, blank=True)

    frame_columns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_default_table',
        verbose_name=_('Frame columns')
    )
    doc_uuid = models.UUIDField(editable=False, unique=True,
                                null=True)
    document_logo = models.ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)

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
        'table.DefaultTableUsercell',
        related_name='of_table_frame',
        blank=True)

    class Meta:
        db_table = "table_frames"
        ordering = ['id']
        verbose_name = _('Tableframe')
        verbose_name_plural = _('Tableframes')

    def __str__(self):
        return f'Table frame#{self.id}'


class DefaultTableUsercell(models.Model):
    frame_id = models.ForeignKey(
        DefaultTableFrame,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Frame')
    )
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('Owner'))
    host_usercolumn = models.ForeignKey(
        UserColumn,
        on_delete=models.CASCADE,
        null=True,
        related_name='table_cells',
        verbose_name=_('User column'))
    cell_content = models.TextField(_('Content'), blank=True, default="", max_length=1000)
    choice_id = models.ForeignKey(
        UserChoice,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Choice id')
    )
    choices_id = ArrayField(
        models.IntegerField(blank=True),
        blank=True,
        default=list,
        verbose_name=_('Choices id')
    )

    class Meta:
        db_table = 'table_usercolumns_contents'
        ordering = ['id']
        verbose_name = _('Table usercolumn data')
        verbose_name_plural = _('Table usercolumn data')

    def __str__(self):
        return f'CELL#{self.id}'


class UsercellFile(models.Model, ResizeImageMixin):
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    host_usercell = models.ForeignKey(
        DefaultTableUsercell,
        on_delete=models.SET_NULL,
        null=True,
        related_name='files'
    )
    file = models.FileField(
        upload_to='usercell_files/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is None and self.file:
            self.resize(self.file, (1920, 1080))
        super().save(*args, **kwargs)


register(DefaultTableModel, permissions)
register(DefaultTableUsercell, permissions)
register(DefaultTableFrame, permissions)
register(UsercellFile, permissions)
