import uuid

from django.db.models import ImageField
from django.utils.translation import gettext_lazy as _
from django.db import models

from accounts.models import ResizeImageMixin
from common.models import PpmDocModel, permissions
from objectpermissions.registration import register
from utils import get_doc_upload_path


class Storyboard(PpmDocModel):
    host_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='storyboards',
        verbose_name=_('Project'))
    # frames
    # chronos
    frame_columns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_storyboard',
        verbose_name=_('Frame columns')
    )
    doc_uuid = models.UUIDField(editable=False, unique=True,
                                null=True)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='storyboards',
        verbose_name=_('Folder'),
        blank=True, null=True
    )

    class Meta:
        db_table = "ppm_storyboards"
        ordering = ['id']
        verbose_name = _('Storyboard')
        verbose_name_plural = _('Storyboards')

    def __str__(self):
        return f'SB#{self.id}'

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)


class Frame(PpmDocModel):
    host_storyboard = models.ForeignKey(
        Storyboard,
        on_delete=models.CASCADE,
        related_name='frames',
        verbose_name=_('Storyboard'))
    duration = models.TimeField(default="00:00")
    userfields = models.ManyToManyField(
        'common.UserCell',
        related_name='of_frame',
        blank=True)

    # shots

    class Meta:
        db_table = "ppm_storyboards_frames"
        ordering = ['id']
        verbose_name = _('Frame')
        verbose_name_plural = _('Frames')

    def __str__(self):
        return f'FRAME#{self.id}'


class Shot(PpmDocModel, ResizeImageMixin):
    host_frame = models.ForeignKey(
        Frame,
        on_delete=models.CASCADE,
        related_name='shots')
    file = models.ImageField(
        upload_to=get_doc_upload_path,
        null=True, blank=True, verbose_name=_('File'))

    class Meta:
        db_table = "ppm_storyboards_frames_shots"
        ordering = ['id']
        verbose_name = _('Shot')
        verbose_name_plural = _('Shots')

    def __str__(self):
        return f'SHOT#{self.id}'

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.resize(self.file, (1920, 1080))
        super().save(*args, **kwargs)


class Chrono(PpmDocModel):
    host_storyboard = models.ForeignKey(
        Storyboard,
        on_delete=models.CASCADE,
        related_name='chronos')

    # chronoframes

    class Meta:
        db_table = "ppm_storyboards_chronos"
        ordering = ['id']
        verbose_name = _('Footage version')
        verbose_name_plural = _('Footage versions')

    def __str__(self):
        return f'CHR#{self.id}'


class ChronoFrame(PpmDocModel):
    sbdframe = models.ForeignKey(
        Frame,
        on_delete=models.CASCADE,
        related_name='in_chronframes'
    )
    host_chrono = models.ForeignKey(
        Chrono,
        on_delete=models.CASCADE,
        related_name='chronoframes'
    )

    class Meta:
        db_table = 'ppm_storyboards_chronoframes'
        ordering = ['id']
        verbose_name = _('Footage frame')
        verbose_name_plural = _('Footage frames')


register(Storyboard, permissions)
register(Chrono, permissions)
register(Frame, permissions)
register(Shot, permissions)
register(ChronoFrame, permissions)
