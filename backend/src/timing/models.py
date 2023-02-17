import uuid

from django.db.models import ImageField

from common.models import PpmDocModel, permissions
from django.utils.translation import gettext_lazy as _
from django.db import models

from objectpermissions.registration import register
from projects.models import Project
from utils import get_doc_upload_path


class Timing(PpmDocModel):
    host_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='timings',
        verbose_name=_('Project'))
    doc_uuid = models.UUIDField(editable=False, unique=True,
                                null=True)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='timings',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    # groups
    # events

    class Meta:
        db_table = "ppm_timing"
        ordering = ['id']
        verbose_name = _('Timing')
        verbose_name_plural = _('Timings')

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Timing#{self.id}'


class TimingGroup(PpmDocModel):
    host_timing = models.ForeignKey(
        'timing.Timing',
        on_delete=models.CASCADE,
        related_name='timing_group',
        verbose_name=_('Timing'))

    class Meta:
        db_table = "ppm_timing_group"
        ordering = ['id']
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def __str__(self):
        return f'Group#{self.id}'


class Event(PpmDocModel):
    host_group = models.ForeignKey(
        'timing.TimingGroup',
        on_delete=models.CASCADE,
        related_name='timing_event',
        verbose_name=_('Group'))
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    class Meta:
        db_table = "ppm_timing_event"
        ordering = ['id']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return f'Event#{self.id}'


register(Timing, permissions)
register(TimingGroup, permissions)
register(Event, permissions)
