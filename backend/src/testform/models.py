from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from common.models import PpmDocModel, permissions
from objectpermissions.registration import register
from django.contrib.postgres.fields import ArrayField

from testform.schema.utils import QTYPE, ANSWER_TYPE, LOGO_CHOICE, get_question_logo_default
from utils import get_doc_upload_path


class TestForm(PpmDocModel):
    """
    Основная форма шаблона теста
    """
    time_to_answer = models.PositiveIntegerField(default=120, verbose_name=_("duration by test"))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='testforms',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    last_open = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    document_logo = models.ImageField(upload_to=get_doc_upload_path,
                                      null=True, blank=True,
                                      verbose_name=_('Document logo'))

    class Meta:
        db_table = 'testform'
        verbose_name_plural = _('testforms')
        ordering = ['-id']
        indexes = [
            models.Index(fields=['owner', 'id'])
        ]

    def __str__(self):
        return f"Test №{self.id}"


class TestFormQuestion(models.Model):
    """
    Основная модель вопроса.
    """
    question_id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=100,
                                     choices=QTYPE,
                                     default="BaseTFQuestion",
                                     verbose_name=_("question type"))
    caption = models.CharField(max_length=200,
                               verbose_name=_("question text"),
                               default="",
                               null=True, blank=True)
    description = models.CharField(max_length=512,
                                   verbose_name=_("question description"),
                                   null=True, blank=True)
    testform = models.ForeignKey(TestForm, on_delete=models.CASCADE)
    require = models.BooleanField(default=True)
    logo_question = models.CharField(max_length=50,
                                     choices=LOGO_CHOICE,
                                     blank=True, null=True)
    url_name = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to=get_doc_upload_path,
                              blank=True,
                              null=True)

    class Meta:
        db_table = 'testform_question'
        verbose_name_plural = _('testform_questions')
        indexes = [
            models.Index(fields=['testform'])
        ]

    def __str__(self):
        return f"Question for {self.testform}"


class TFQuestionType(models.Model):
    """
    Модель типа вопроса
    """
    testform_question = models.ForeignKey(TestFormQuestion, on_delete=models.CASCADE)
    order_id = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.order_id == 0:
            last = self.__class__.objects.only('order_id').order_by('order_id').last() or 0
            self.order_id = last.order_id + 1 if last != 0 else 1
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        db_table = 'tf_question_type'
        verbose_name_plural = _('tf_question_types')
        indexes = [
            models.Index(fields=['testform_question'])
        ]


class BaseTFQuestion(TFQuestionType):
    """
    Модель основного вопроса, наследована от TFQuestionType
    """
    answer_type = ArrayField(models.CharField(max_length=10,
                                              choices=ANSWER_TYPE,
                                              blank=True),
                             size=2,
                             default=get_question_logo_default)
    max_time = models.PositiveIntegerField(default=120, null=True, blank=True)


class FinalTFQuestion(TFQuestionType):
    """
    Модель завершающего вопроса, наследована от TFQuestionType
    """
    button_name = models.CharField(max_length=250, null=True, blank=True, default=_('Новый ответ'))


register(TestForm, permissions)
register(TestFormQuestion, permissions)
