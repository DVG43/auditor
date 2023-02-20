import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import ImageField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from accounts.models import ResizeImageMixin
from contacts.models import Contact
from objectpermissions.registration import register
from common.models import PpmDocModel, permissions
from utils import get_upload_path, get_doc_upload_path


class Project(PpmDocModel, ResizeImageMixin):
    logo = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        verbose_name=_('Logo')
    )
    contacts = models.ManyToManyField(
        Contact,
        related_name='in_projects',
        blank=True,
        verbose_name=_('Crew members')
    )
    doc_order = ArrayField(
        models.UUIDField(null=True), blank=True,
        default=list, verbose_name=_('Frame order'))
    # storyboards
    # links

    class Meta:
        db_table = 'ppm_projects'
        ordering = ['id']
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return f'PRJ#{self.id}'

    def save(self, *args, **kwargs):
        if self.pk is None and self.logo:
            self.resize(self.logo, (200, 200))
        super().save(*args, **kwargs)


class Link(PpmDocModel):
    host_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='links')
    url = models.URLField(_('Url'), max_length=255)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name=_('Folder'),
        blank=True, null=True
    )

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)


class File(PpmDocModel):
    host_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(_('File'), upload_to=get_doc_upload_path)
    slugged_name = models.SlugField(_('Filename'), null=True)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Folder'),
        blank=True, null=True
    )

    def save(self, *args, **kwargs):
        self.slugged_name = slugify(self.name)
        if not self.order_id:
            self.order_id = uuid.uuid4()
        super(File, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        return super().delete()

    class Meta:
        ordering = ['id']
        unique_together = ['name', 'file', 'host_project']


class Text(PpmDocModel):
    host_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='texts')
    text = models.CharField(_('Text'), max_length=1000)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='texts',
        verbose_name=_('Folder'),
        blank=True, null=True
    )

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)


register(Project, permissions)
