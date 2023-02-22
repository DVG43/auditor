from http import HTTPStatus

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status

from poll.models.surveypassing import SurveyPassing
from poll.serializers.answer import UserAnswerSerializer
from poll.serializers.surveypassing import SurveyPassingSerializer
# from user.views import user
from poll.paginations import SurveyPassingPagination


class SurveyPassingCollectionSet(APIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = SurveyPassing.objects.all().select_related("user").prefetch_related(
            "useranswerquestion_set",
            "poll__telegramintegration",
            "poll__manyfromlistquestion_set__items",
            "poll__freeanswer_set__tags",
            "poll__freeanswer_set__attached_type",
            "poll__freeanswer_set__items__tags",
            "poll__yesnoquestion_set__items",
            "poll__yesnoquestion_set__yes_no_answers",
            "poll__yesnoquestion_set__attached_type",
            "poll__mediaquestion_set__attached_type",
            "poll__mediaquestion_set__items",
        )
        return queryset

    def get(self, request, pk=None, survey=None):
        queryset = self.get_queryset().filter(poll_id=pk, status='finished')
        pagination = SurveyPassingPagination()
        page = pagination.paginate_queryset(queryset=queryset, request=self.request)
        if page is not None:
            serializer = SurveyPassingSerializer(page, many=True)
            return pagination.get_paginated_response(serializer.data)

        serializer = SurveyPassingSerializer(queryset, many=True)
        return pagination.get_paginated_response(serializer.data)

    def post(self, request, pk=None, format=None):
        # if not request.user:
        #     request.user = user.User.get_user_by_email('ano@nymo.us')
        #     # request.user = request.META['REMOTE_ADDR']

        try:
            serialized_survey_passing = SurveyPassingSerializer(request.data)

            if serialized_survey_passing.is_valid:
                new_sp = serialized_survey_passing.create(request.user, request.data)

                new_sp.save()
                if 'user_answers' in request.data:
                    serialized_user_answers = UserAnswerSerializer(request.data['user_answers'], many=True)
                    if serialized_user_answers.is_valid:
                        for x in request.data['user_answers']:
                            x['survey_id'] = new_sp.pk
                        serialized_user_answers.create(request.data['user_answers'])
        except Exception as er:
            return Response({'error': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The survey passing has been created', 'survey_id': '{}'.format(new_sp.pk)},
                        status=HTTPStatus.OK)


class SurveyIdPassingCollectionSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None, survey=None):
        survey_passings = SurveyPassing.objects.filter(id=pk)
        serialized_survey_passings = SurveyPassingSerializer(survey_passings, many=True)
        return Response({'survey_Passing': serialized_survey_passings.data},
                        status=HTTPStatus.OK)

    def post(self, request, pk=None, format=None):

        # if not request.user:
        #     request.user = user.User.get_user_by_email('ano@nymo.us')
        try:
            serialized_survey_passing = SurveyPassingSerializer(request.data)

            if serialized_survey_passing.is_valid:
                new_sp = serialized_survey_passing.create(request.user, request.data)
                new_sp.save()
                if 'user_answers' in request.data:
                    serialized_user_answers = UserAnswerSerializer(request.data['user_answers'], many=True)
                    if serialized_user_answers.is_valid:
                        for x in request.data['user_answers']:
                            x['survey_id'] = new_sp.pk
                        serialized_user_answers.create(request.data['user_answers'])
        except Exception as er:
            return Response({'error': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The survey passing has been created', 'survey_id': '{}'.format(new_sp.pk)},
                        status=HTTPStatus.OK)


class SurveyPassingMultipleDelete(APIView):
    queryset = SurveyPassing.objects.all()
    serializer_class = SurveyPassingSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        delete_ids = request.query_params.get('survey_ids', None)
        if not delete_ids:
            return Response(status=status.HTTP_404_NOT_FOUND)
        for i in delete_ids.split(','):
            get_object_or_404(SurveyPassing, pk=int(i)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
