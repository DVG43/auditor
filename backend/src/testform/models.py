from django.db import models
from django.utils.translation import gettext_lazy as _


class TestForm(PpmDocModel):
    id = models.AutoField(primary_key=True)
    seconds_time = models.PositiveIntegerField(default=120, verbose_name=_("время для прохождения"))
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='polls',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    test_logo = ImageField(upload_to=get_doc_upload_path,
                           null=True, blank=True,
                           verbose_name=_('TestForm logo'))


class TFQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=100,
                                     default='MainQuestion',
                                     verbose_name=_("тип вопроса"))
    order_id = models.PositiveIntegerField(default=1)
    caption = models.CharField(max_lenth=200, verbose_name=_("текст вопроса"))
    description = models.CharField(max_length=512,
                                   verbose_name=_("описание вопроса"),
                                   null=True, blank=True)
    testform = models.ForeignKey(TestForm, on_delete=models.CASCADE)
    require = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    # mix_answers = models.BooleanField(default=False)
    # time_for_answer = models.BooleanField(default=False)
    # type_for_show = models.IntegerField(default=0)
    # title_image = models.CharField(max_length=512, default='')
    # resize_image = models.BooleanField(default=False)
    # test_mode = models.BooleanField(default=False)


    class Meta:
        abstract = True
        ordering = ['-updated_at']

    def _update_or_related_objects(self, objects_list, related_name, primary_key_name, model):
        for obj in objects_list:
            obj_id = obj.pop(primary_key_name, None)
            obj_id = int(obj_id) if obj_id else None
            obj, created = model.objects.update_or_create(
                pk=obj_id,
                defaults={**obj},
            )
            getattr(self, related_name).add(obj)
        self.save()
        return getattr(self, related_name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, sort=True):
        # if self.poll.telegram_integration_is_active():
        #     self.poll.telegramintegration.update_variable_in_message()

        result = super(Question, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )
        return result

    @staticmethod
    def normalize_order_id(query_set):
        for i, v in enumerate(query_set.all(), start=1):
            v.order_id = i
            v.save()
        return query_set


class MainQuestion(TFQuestion):
    ANSWER_TYPE = (
        ('text', 'text'),
        ('video', 'video'),
    )
    type_answer = models.ArrayField(models.CharField(max_lenth=10, choices=ANSWER_TYPE))
#
# class TFQuestion(models.Model):
#     ANSWER_TYPE = (
#         ('text', 'text'),
#         ('video', 'video'),
#     )
#     number = models.PositiveIntegerField(default=1)
#     testform = models.ForeignKey(TestForm, ondelete=models.CASCADE)
#     required = models.BooleanField(default=False)
#     description = models.CharField(max_lenth=250, blank=True, null=True)
#     answer_type = models.CharField(max_lenth=100, chioces=ANSWER_TYPE)
#     poster = models.FileField(upload_to=None, max_length=254, blank=True, null=True)
#
#     class Meta:
#         unique_together = ('storyboard', 'number')
#         verbose_name_plural = _('storyboard_questions')
#         ordering = ['number', ]
#


class FinalTFQuestion(TFQuestion):
    description_mode = models.BooleanField(default=False)
    max_video_duration = models.IntegerField(default=0, blank=False, null=False)
    is_video = models.BooleanField(default=False)
    items = models.ManyToManyField(ItemQuestion)

    show_my_answers = models.BooleanField(default=False)
    correct_answers = models.BooleanField(default=False)
    point_for_answers = models.BooleanField(default=False)
    button_mode = models.BooleanField(default=False)
    button_text = models.CharField(max_length=512, default='', blank=True, null=True)
    button_url = models.CharField(max_length=512, default='', blank=True, null=True)
    reopen = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(FinalTFQuestion, self).__init__(*args, **kwargs)
        self.question_type = __class__.__name__

    class Meta:
        db_table = 'testform_final_question'
        verbose_name_plural = 'testform_final_questions'
        indexes = [
            models.Index(fields=['testform'])
        ]
