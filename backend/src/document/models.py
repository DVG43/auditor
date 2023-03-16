from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from projects.models import Project
from common.models import PpmDocModel, permissions
from django.utils.translation import gettext_lazy as _
from utils import get_doc_upload_path
from django.contrib.postgres.fields import ArrayField
from objectpermissions.registration import register
import uuid


class Document(PpmDocModel):
    owner = models.ForeignKey(
        'accounts.User', verbose_name=_('Owner'), related_name="documents", on_delete=models.CASCADE)
    host_project = models.ForeignKey(
        Project,
        related_name="documents",
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    doc_uuid = models.UUIDField(editable=False, unique=True, null=True)
    order_id = models.UUIDField(null=True, unique=True, default=uuid.uuid4)
    document_logo = models.ImageField(upload_to=get_doc_upload_path,
                                      null=True, blank=True, verbose_name=_('Document logo'))
    parent = models.ForeignKey(
        'self', verbose_name=_('Родитель'), on_delete=models.SET_NULL, blank=True, null=True, related_name="children"
    )
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    doc_order = ArrayField(
        models.UUIDField(null=True), blank=True,
        default=list, verbose_name=_('Document order'))
    content = models.TextField(verbose_name=_("Контент"), default="")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'ppm_documents'
        ordering = ['created_at']

class Element(models.Model):
    document_id = models.ForeignKey(Document, related_name="element", on_delete=models.CASCADE)
    content = models.TextField("контент")

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['id']
        db_table = 'ppm_documents_elements'


class TagForDocument(models.Model):
    document_id = models.ForeignKey(Document, related_name="tag", on_delete=models.CASCADE)
    word = models.CharField(max_length=100)

    def __str__(self):
        return self.word

    class Meta:
        db_table = 'ppm_documents_tags'


register(Document, permissions)
register(Element, permissions)
register(TagForDocument, permissions)
