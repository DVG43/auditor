from django.db import models
from jsonfield import JSONField
from django.conf import settings
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
import json
import google.auth.exceptions

from poll.models.poll import Poll
from accounts.models import User
from poll.models.surveypassing import SurveyPassing


class GoogleSheetIntegration(models.Model):
    id = models.OneToOneField(Poll, primary_key=True, on_delete=models.CASCADE,
                              verbose_name='poll id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    is_active = models.BooleanField(default=False,
                                    verbose_name='active')
    spreadsheet_id = models.CharField(max_length=255, default='', blank=True, null=True,
                                      verbose_name='spreadsheetId')
    spreadsheet_url = models.URLField(blank=True, null=True,
                                      verbose_name='spreadsheet url')
    row_count = models.PositiveIntegerField(default=1, verbose_name='row count')
    survey_id = models.ManyToManyField(SurveyPassing, blank=True, verbose_name='survey_id')

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'GoogleSheetIntegration'
        verbose_name_plural = 'GoogleSheetIntegrations'

    def __str__(self):
        return repr(self.id)


class GoogleSheetCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_sheet_credetials = JSONField(default='', blank=True, null=True)

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'GSCredentials'
        verbose_name_plural = 'GSCredentials'

    def __str__(self):
        return repr(self.id)

    @staticmethod
    def get_google_auth_url(credentials_fname):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            credentials_fname,
            scopes=['https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'openid'])
        flow.redirect_uri = f'{settings.DOMAIN}/v1/googleauth/creategooglesheet/'

        return flow.authorization_url(access_type='offline',
                                      prompt='consent',
                                      include_granted_scopes='true')

    def create_connection(self, request, credentials_fname):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            credentials_fname,
            scopes=['https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'openid'], )

        flow.redirect_uri = f'{settings.DOMAIN}/v1/googleauth/creategooglesheet/'

        authorization_response = request.build_absolute_uri('/') + request.get_full_path()

        if authorization_response[:5] != 'https':
            authorization_response = 'https' + authorization_response[4:]

        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        self.google_sheet_credetials = credentials.to_json()

        self.save()
        return self.google_sheet_credetials

    def refresh_token(self, request):

        credentials = Credentials.from_authorized_user_info(
            json.loads(self.google_sheet_credetials))
        request_auth = google.auth.transport.requests.Request()

        try:
            credentials.refresh(request_auth)
            self.google_sheet_credetials = credentials.to_json()
        except google.auth.exceptions.RefreshError:
            self.google_sheet_credetials = ''

        self.save()
        return self.google_sheet_credetials
