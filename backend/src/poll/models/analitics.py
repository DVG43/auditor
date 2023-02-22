from django.db import models
from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing


class PollAnalitics(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='id')
    poll_id = models.OneToOneField(Poll, on_delete=models.CASCADE, verbose_name='poll id')
    survey_id = models.ManyToManyField(SurveyPassing, blank=True, verbose_name='survey_id')
    avarage_age = models.FloatField(default=0, verbose_name='Avarage age')
    men_total = models.PositiveIntegerField(default=0, verbose_name='Total men')
    women_total = models.PositiveIntegerField(default=0, verbose_name='Total women')
    women_before_18 = models.PositiveIntegerField(default=0, verbose_name='Women before 18')
    men_before_18 = models.PositiveIntegerField(default=0, verbose_name='Men before 18')
    women_in_18_24 = models.PositiveIntegerField(default=0, verbose_name='Women between 18 and 24')
    men_in_18_24 = models.PositiveIntegerField(default=0, verbose_name='Men between 18 and 24')
    women_in_25_35 = models.PositiveIntegerField(default=0, verbose_name='Women between 25 and 35')
    men_in_25_35 = models.PositiveIntegerField(default=0, verbose_name='Men between 25 and 35')
    women_in_36_45 = models.PositiveIntegerField(default=0, verbose_name='Women between 36 and 45')
    men_in_36_45 = models.PositiveIntegerField(default=0, verbose_name='Men between 36 and 45')
    women_older_46 = models.PositiveIntegerField(default=0, verbose_name='Women older 46')
    men_older_46 = models.PositiveIntegerField(default=0, verbose_name='Men older 46')
    from_desktop = models.PositiveIntegerField(default=0, verbose_name='From desktop')
    from_mobile = models.PositiveIntegerField(default=0, verbose_name='From mobile')
    from_other = models.PositiveIntegerField(default=0, verbose_name='From other')

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Analitics'
        verbose_name_plural = 'Analitics'

    def __str__(self):
        return repr(self.id)
