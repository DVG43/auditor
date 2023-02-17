import os
import uuid
import settings

from django.db import models
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from common.models import PpmDocModel, permissions
from objectpermissions.registration import register
from utils import get_doc_upload_path


class Shootingplan(PpmDocModel):
    host_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='shootingplans',
        verbose_name=_('Project')
    )
    date = models.DateField(_('Date'))
    doc_uuid = models.UUIDField(editable=False, unique=True,
                                null=True)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='shootingplans',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    # units

    class Meta:
        db_table = "ppm_shootingplans"
        ordering = ['id']
        verbose_name = _('Shootingplan')
        verbose_name_plural = _('Shootingplans')

    def __str__(self):
        return f'SHP#{self.id}'

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)


class Unit(PpmDocModel):
    host_shootingplan = models.ForeignKey(
        Shootingplan,
        on_delete=models.CASCADE,
        related_name='units')
    day_start = models.TimeField(default="00:00")
    name = models.CharField(max_length=50, default="Юнит")
    # unitframes
    frame_columns = models.ManyToManyField(
        'common.UserColumn',
        blank=True,
        related_name='of_unit'
    )

    class Meta:
        db_table = "ppm_shootingplans_units"
        ordering = ['id']
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')

    def __str__(self):
        return f'UNIT#{self.id}'


class Unitframe(PpmDocModel):
    host_unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='unitframes'
    )
    duration = models.TimeField(default="00:00")
    sbdframe = models.ForeignKey(
        'storyboards.Frame',
        on_delete=models.CASCADE,
        null=True,
        related_name='in_unitframes'
    )
    userfields = models.ManyToManyField(
        'common.UserCell',
        blank=True,
        related_name='of_unitframe'
    )

    class Meta:
        db_table = "ppm_shootingplans_unitframes"
        ordering = ['id']
        verbose_name = _('Unit frame')
        verbose_name_plural = _('Unit frames')

    def __str__(self):
        return f'UNITFRAME#{self.id}'


register(Shootingplan, permissions)
register(Unit, permissions)
register(Unitframe, permissions)


@receiver(post_save, sender=Shootingplan)
def update_image_path(sender, instance, created, **kwargs):
    """Updates a Shootingplan document_logo path dnd name.
        While Shootingplan creating upload_to creates a path where document_logo of all
        Shootingplans are in the 'None' folder.
        This signal corrects a flaw and places the document_logo file in the correct folder.

        Example:
            '10/shootingplan/None/orig.png' -> '10/shootingplan/1/orig.png'
            where 1 - shootingplan.id
    """
    try:
        if created and instance.document_logo:
            imagefile = instance.document_logo
            new_name = get_doc_upload_path(instance, imagefile.name.split('/')[-1])
            new_path = os.path.join(settings.MEDIA_ROOT, new_name)
            if not os.path.exists(new_path):
                os.makedirs(os.path.dirname(new_path))
            os.rename(imagefile.path, new_path)
            instance.document_logo.name = new_name
            instance.save()
    except AttributeError:
        pass
