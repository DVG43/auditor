import uuid
from operator import attrgetter

from django.db import models
from jsonfield import JSONField
from django.utils.translation import gettext_lazy as _
from django.db.models import ImageField

from accounts.models import User
from common.models import PpmDocModel, permissions
from objectpermissions.registration import register
from utils import get_doc_upload_path


class PollTags(models.Model):
    class Meta:
        db_table = 'poll_tags'
        verbose_name_plural = 'polls_tags'

    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(default='tag',  blank=False, null=False, max_length=32)


class Poll(PpmDocModel):
    """
    Poll
    """
    id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # title = models.CharField(max_length=200, default='')
    image = models.CharField(max_length=200, default='')
    test_mode_global = models.BooleanField(default=False)
    count_answers = models.PositiveIntegerField(default=0)
    tags_list = models.ManyToManyField(PollTags)
    last_open = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='polls',
        verbose_name=_('Folder'),
        blank=True, null=True
    )
    order_id = models.UUIDField(
        null=True,
        unique=True,
        default=uuid.uuid4
    )
    document_logo = ImageField(upload_to=get_doc_upload_path,
                               null=True, blank=True,
                               verbose_name=_('Document logo'))

    class Meta:
        db_table = 'poll'
        verbose_name_plural = 'polls'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['owner'])
        ]

    def delete(self, using=None, keep_parents=False):
        for d in self.divisionquestion_set.all():
            d.delete()
        for d in self.yesnoquestion_set.all():
            d.delete()
        super(Poll, self).delete()

    def new_survey_passing(self):
        return self.surveypassing_set.filter(
            created_at__gte=self.last_open,
            status='finished'
        ).count()

    # def telegram_integration_is_active(self):
    #     try:
    #         return self.telegramintegration.is_active
    #     except:
    #         return False
    #
    # def googlesheet_integration_is_active(self):
    #     try:
    #         return self.googlesheetintegration.is_active
    #     except:
    #         return False

    def obj_url(self, requests):
        poll_url = requests.build_absolute_uri(f'/completing-survey/{self.pk}')
        if poll_url[:5] != 'https':
            poll_url = 'https' + poll_url[4:]
        return poll_url

    def obj_report_url(self, requests):
        poll_url = requests.build_absolute_uri(f'/report-page/{self.pk}')
        if poll_url[:5] != 'https':
            poll_url = 'https' + poll_url[4:]
        return poll_url

    def get_questions(self, sort=True):
        questions = []
        if self.divisionquestion_set:
            questions.extend(list(self.divisionquestion_set.all()))
        if self.yesnoquestion_set:
            questions.extend(list(self.yesnoquestion_set.all()))
        if self.manyfromlistquestion_set:
            questions.extend(list(self.manyfromlistquestion_set.all()))
        if self.textquestion_set:
            questions.extend(list(self.textquestion_set.all()))
        if self.ratingquestion_set:
            questions.extend(list(self.ratingquestion_set.all()))
        if self.mediaquestion_set:
            questions.extend(list(self.mediaquestion_set.all()))
        if self.headingquestion_set:
            questions.extend(list(self.headingquestion_set.all()))
        if self.freeanswer_set:
            questions.extend(list(self.freeanswer_set.all()))
        if self.finalquestion_set:
            questions.extend(list(self.finalquestion_set.all()))

        if sort:
            questions = sorted(questions, key=attrgetter('order_id'))
        return questions

    def normalize_questions_order_id(self):
        questions = self.get_questions(sort=False)
        questions = sorted(questions, key=lambda x: (x.order_id, -x.updated_at.timestamp()))

        _questions = questions.copy()
        index = 0
        questions_for_update = {}
        for i, v in enumerate(_questions, start=1):
            key = v.__class__.__name__
            prev_data = questions_for_update.get(key, [])
            if v.question_type == 'FinalQuestion':
                questions.remove(v)
                v.order_id = len(_questions) + 1
                index -= 1
            else:
                v.order_id = i + index
            questions_for_update[key] = [*prev_data, v]

        for key in questions_for_update.keys():
            question_model = questions_for_update[key][0].__class__
            question_model.objects.bulk_update(questions_for_update[key], ["order_id"])

        return questions


class PollSettings(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE, primary_key=True,
                                related_name='setting')

    isFormActive = models.BooleanField(default=True)
    mixQuestions = models.BooleanField(default=False)
    allowRefillingForm = models.BooleanField(default=True)
    groupsForRefilling = JSONField(default=[], null=True, blank=True)
    groupsForOnlyOneFilling = JSONField(default=[], null=True, blank=True)
    usePassword = models.BooleanField(default=False)
    formPassword = models.CharField(max_length=128, default=None, blank=True, null=True)
    useAnswersCountRestriction = models.BooleanField(default=False)
    maxAnswers = models.CharField(default='0', max_length=80, blank=True, null=True)
    useAnswersTimeRestriction = models.CharField(max_length=12, default='')
    maxTimeRange = JSONField(default=['', ''], null=True, blank=True)
    isRedirectActive = models.BooleanField(default=False)
    redirectMethod = models.CharField(max_length=128, default='', blank=False, null=False)
    redirectPath = models.CharField(max_length=128, default='', blank=False, null=False)
    askLocation = models.BooleanField(default=False)
    activeCaptcha = models.BooleanField(default=False)
    useSignature = models.BooleanField(default=False)
    reopenForm = models.BooleanField(default=False)
    reopenDelay = models.CharField(default='90', max_length=80)
    formInactiveMessage = models.CharField(max_length=200, default='')
    language = models.CharField(max_length=20, default='')
    externalapi = models.CharField(max_length=200, blank=True, null=True)
    externalapiparams = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'poll_settings'
        verbose_name_plural = 'polls_settings'


register(Poll, permissions)
register(PollSettings, permissions)
