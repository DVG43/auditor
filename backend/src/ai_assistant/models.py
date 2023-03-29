from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import permissions, PpmDocModel
from folders.models import Folder
from objectpermissions.registration import register
# Create your models here.


class AiAssistant(PpmDocModel):
    folder = models.ForeignKey(Folder, related_name="tables", on_delete=models.CASCADE,
                               null=True, blank=True)

    class Meta:
        db_table = 'ai_assistant'
        verbose_name_plural = 'ai_assistants'
        indexes = [
            models.Index(fields=['id'])
        ]


class Source(models.Model):
    id = models.AutoField(primary_key=True)
    ai_assistant = models.ForeignKey(
        AiAssistant,
        verbose_name=_('AI Assistant'),
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class InnerSource(Source):
    doc_id = models.IntegerField(
        _('Document ID')
    )
    model = models.CharField(
        _('Model'),
        max_length=25,
    )

    class Meta:
        db_table = 'inner_source'
        verbose_name_plural = 'inner_sources'
        indexes = [
            models.Index(fields=['id'])
        ]


class OuterSource(Source):
    link = models.URLField(_('Link'), max_length=255)
    description = models.TextField(
        _('Description'),
        blank=True,
        max_length=1000
    )

    class Meta:
        db_table = 'outer_source'
        verbose_name_plural = 'outer_sources'
        indexes = [
            models.Index(fields=['id'])
        ]


register(AiAssistant, permissions)
