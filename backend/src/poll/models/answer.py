from django.db import models
from django.contrib.postgres.fields import ArrayField

from poll.fields import SimpleJsonField
from poll.models.surveypassing import SurveyPassing
from accounts.models import User


class AnswerQuestion(models.Model):
    event_choices = (
        ('NEW', 'New'),
        ('STARTED', 'Started'),
        ('INPROGRESS', 'In progress'),
        ('COMPLETED', 'Completed'),)

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll_id = models.IntegerField(blank=False, null=False)
    question_id = models.IntegerField(blank=False, null=False)

    survey = models.ForeignKey(SurveyPassing, on_delete=models.CASCADE, default=1)

    question_type = models.CharField(max_length=100, default='NoType')
    text = models.CharField(max_length=500, default=None, blank=True, null=True)
    checked = models.BooleanField(default=None, blank=True, null=True)
    photo_path = models.CharField(max_length=500, default=None, blank=True, null=True)
    items_question = ArrayField(ArrayField(models.IntegerField()), blank=True, null=True)  # выбор элементов из списка в вопросе
    platform = models.CharField(max_length=100, default='Desktop')
    age = models.IntegerField(blank=True, null=True)
    during = models.IntegerField(blank=True, null=True, default=1)
    sex = models.CharField(max_length=10, blank=True, null=True, default=None)
    event = models.CharField(max_length=15, choices=event_choices, default='new')
    class Meta:
        db_table = 'poll_answer_question'
        #ordering = ['number']
        verbose_name_plural = 'poll_answer_questions'


class UserAnswerQuestion(models.Model):

    class Meta:
        db_table = 'poll_user_answers'
        verbose_name_plural = 'poll_user_answers'

    event_choices = (
        ('NEW', 'New'),
        ('STARTED', 'Started'),
        ('INPROGRESS', 'In progress'),
        ('COMPLETED', 'Completed'),)

    survey = models.ForeignKey(SurveyPassing, on_delete=models.CASCADE)
    question_id = models.IntegerField(blank=False, null=False)
    text = models.CharField(max_length=500, default=None, blank=True, null=True)
    date = models.DateTimeField(default=None, blank=True, null=True)
    number = models.FloatField(default=None, blank=True, null=True)
    checked = models.BooleanField(default=None, blank=True, null=True)
    poll_id = models.IntegerField(blank=False, null=True, default=None)
    items_question = ArrayField(ArrayField(models.IntegerField()), blank=True, null=True)  # выбор элементов из списка в вопросе
    event = models.CharField(max_length=15, choices=event_choices, default='new')
    during = models.IntegerField(blank=True, null=True, default=1)
    another_answer = models.CharField(max_length=1500, default=None, blank=True, null=True)

    video_answer = SimpleJsonField(default=None, blank=True, null=True)
    accepted = models.BooleanField(default=False)
    points = models.IntegerField(default=0)

    question_type = models.CharField(max_length=100, null=True, blank=True)
    photo_answer = SimpleJsonField(default=None, blank=True, null=True)
    audio_answer = SimpleJsonField(default=None, blank=True, null=True)
    file_answer = SimpleJsonField(default=None, blank=True, null=True)
    text_answer = SimpleJsonField(default=None, blank=True, null=True)
    yes_no_answers_id = ArrayField(models.IntegerField(null=True), blank=True, null=True)
