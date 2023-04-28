from django.db import models

from poll.models.poll import Poll


class SurveyPassing(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    answers = models.JSONField(default=list, blank=True, null=True)

    class Meta:
        db_table = 'poll_surveypassing'
        verbose_name_plural = 'poll_surveypassings'

    # def obj_report_url(self, requests):
    #     poll_url = requests.build_absolute_uri(f'/report-page/{self.pk}')
    #     if poll_url[:5] != 'https':
    #         poll_url = 'https' + poll_url[4:]
    #     return poll_url


# class UserSurveyPassingRating(models.Model):
#     class Meta:
#         unique_together = (('user', 'survey_passing'),)
#     user = models.ForeignKey(SecretGuestProfile, on_delete=models.CASCADE)
#     survey_passing = models.ForeignKey(SurveyPassing, on_delete=models.CASCADE)
#     score = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
