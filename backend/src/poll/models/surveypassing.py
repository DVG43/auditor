from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from poll.models.poll import Poll
from accounts.models import User # , SecretGuestProfile
from jsonfield import JSONField

class SurveyPassing(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=6, default=None, blank=True, null=True)
    platform = models.CharField(max_length=100, default=None, blank=True, null=True)
    age = models.PositiveIntegerField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(default=None, blank=True, null=True)
    user_name = models.CharField(max_length=100, default='Anonymous')
    survey_title = models.CharField(max_length=255, default='Untitled')
    status = models.CharField(max_length=10, default='new')
    questions = JSONField(default=None, blank=True, null=True)

    class Meta:
        db_table = 'poll_surveypassing'
        verbose_name_plural = 'poll_surveypassings'

    def obj_report_url(self, requests):
        poll_url = requests.build_absolute_uri(f'/report-page/{self.pk}')
        if poll_url[:5] != 'https':
            poll_url = 'https' + poll_url[4:]
        return poll_url


# class UserSurveyPassingRating(models.Model):
#     class Meta:
#         unique_together = (('user', 'survey_passing'),)
#     user = models.ForeignKey(SecretGuestProfile, on_delete=models.CASCADE)
#     survey_passing = models.ForeignKey(SurveyPassing, on_delete=models.CASCADE)
#     score = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
