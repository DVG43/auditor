import json
from django.utils import timezone
from rest_framework import serializers
from google.oauth2.credentials import Credentials

from integration.models.googlesheet import GoogleSheetIntegration
from integration.services.googlesheet import gs_service, sheet_service
from poll.models.poll import Poll
from accounts.models import User


class GoogleSheetIntegrationSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ['id']

    is_active = serializers.BooleanField(default=False, read_only=True)
    row_count = serializers.IntegerField(default=1, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoogleSheetIntegration
        fields = ['url', 'id', 'user', 'is_active',
                  'spreadsheet_url', 'row_count', 'survey_id']

    def create(self, validated_data):
        google_sheet_integration = GoogleSheetIntegration.objects.create(
            user=self.context['SESSION']['user'],
            id=validated_data['id'])
        sheet_name = google_sheet_integration.user.email + '_' + str(validated_data['id'].poll_id)

        credentials = Credentials.from_authorized_user_info(
            json.loads(self.context['request'].session['gs_credentials']))

        service = gs_service.connect_to_google_sheet_api(credentials=credentials)
        spreadsheet = gs_service.create_empty_spreadsheets(service=service, sheet_name=sheet_name)
        gs_service.get_access_to_spreadsheets_for_any_user(
            credentials=credentials, spreadsheet_id=spreadsheet['spreadsheetId']
        )

        google_sheet_integration.spreadsheet_id = spreadsheet["spreadsheetId"]
        google_sheet_integration.spreadsheet_url = spreadsheet["spreadsheetUrl"]
        google_sheet_integration.is_active = True

        poll = Poll.objects.prefetch_related(
            "yesnoquestion_set__items",
            "manyfromlistquestion_set__items",
            "freeanswer_set__items",
            "surveypassing_set__user__secretguestprofile")\
            .get(pk=google_sheet_integration.id.poll_id)

        questions = sheet_service.get_poll_questions(poll=poll)
        spreadsheet_data = sheet_service.get_caption(questions=questions)

        # All answers that were before google sheet integration
        last_month = timezone.now() - timezone.timedelta(days=30)
        for survey in poll.surveypassing_set.filter(created_at__gte=last_month):
            question_row_data, count_user_answer = sheet_service.get_questions_row_data(
                survey=survey, questions=questions
            )
            if count_user_answer == 0:
                continue
            base_row_data = sheet_service.get_base_row_data(
                request=self.context['request'], survey=survey,
                count_question=len(questions), count_answers=count_user_answer
            )
            if not question_row_data:
                continue
            row_data = [*base_row_data, *question_row_data]
            spreadsheet_data.append(row_data)

        list_with_form_link = [
            [""],
            ["Ссылка на форму"],
            [self.context['request'].build_absolute_uri(
                f"/constructor/{validated_data['id'].poll_id}")]
        ]

        spreadsheet_data.extend(list_with_form_link)

        gs_service.add_information_to_spreadsheet(
            sheet_name=sheet_name,
            service=service,
            row_count=google_sheet_integration.row_count,
            spreadsheet_id=google_sheet_integration.spreadsheet_id,
            values=spreadsheet_data
        )

        google_sheet_integration.row_count += len(spreadsheet_data) - len(list_with_form_link)

        gs_service.set_default_format_sheet(
            service=service,
            spreadsheet_id=google_sheet_integration.spreadsheet_id,
            len_spreadsheet_data=len(spreadsheet_data[0])
        )

        google_sheet_integration.save()

        return google_sheet_integration

    def update(self, instance, validated_data):
        survey = validated_data['survey_id'][0]
        if survey in instance.survey_id.all():
            return super(GoogleSheetIntegrationSerializer, self).update(instance, validated_data)

        credentials = Credentials.from_authorized_user_info(
            json.loads(self.context['request'].session['gs_credentials']))
        service = gs_service.connect_to_google_sheet_api(credentials=credentials)

        questions = sheet_service.get_poll_questions(poll=instance.id)

        question_row_data, count_user_answer = sheet_service.get_questions_row_data(
            survey=survey, questions=questions
        )
        base_row_data = sheet_service.get_base_row_data(
            request=self.context['request'], survey=survey,
            count_question=len(questions), count_answers=count_user_answer
        )

        row_data = [*base_row_data, *question_row_data]

        gs_service.update_sheet(
            service=service,
            spreadsheet_id=instance.spreadsheet_id,
            requests={
                "insertDimension": {
                    "range": {
                        "sheetId": 0,
                        "dimension": "ROWS",
                        "startIndex": instance.row_count,
                        "endIndex": instance.row_count + 1
                    },
                    "inheritFromBefore": False
                }
            }
        )

        sheet_name = instance.user.email + '_' + str(validated_data['id'].poll_id)

        gs_service.add_information_to_spreadsheet(
            sheet_name=sheet_name,
            service=service,
            row_count=instance.row_count,
            spreadsheet_id=instance.spreadsheet_id,
            values=[row_data]
        )
        rows_with_captions = sheet_service.get_caption(questions=questions)

        gs_service.add_information_to_spreadsheet(
            sheet_name=sheet_name,
            service=service,
            row_count=1,
            spreadsheet_id=instance.spreadsheet_id,
            values=rows_with_captions
        )

        instance.row_count += 1
        instance.survey_id.add(survey)
        instance.save()
        return instance


class GoogleSheetIntegrationPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleSheetIntegration
        fields = ['url', 'id', 'is_active', 'spreadsheet_url']

    def update(self, pk, instance, *args, **kwargs):
        google_sheet_integration = instance

        google_sheet_integration.is_active = not google_sheet_integration.is_active
        google_sheet_integration.save()
        return google_sheet_integration
