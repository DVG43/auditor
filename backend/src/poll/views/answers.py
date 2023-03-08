import logging

from http import HTTPStatus

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

# from integration.service import survey_passing_event_finish
# from integration.externalapi import externalAPI
from poll.models.answer import AnswerQuestion, UserAnswerQuestion
from poll.models.poll import Poll, PollSettings
from poll.models.surveypassing import SurveyPassing
from poll.serializers.answer import AnswerSerializer, UserAnswerSerializer
from poll.serializers.surveypassing import SurveyPassingSerializer
# from user.views import user

logging.basicConfig(filename=settings.APP_API_LOG, level=logging.INFO)


class AnswerCollectionSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk, slug='my', format=None):
        if slug == 'my':
            answers = AnswerQuestion.objects.filter(user=request.user).all()
        if slug == 'all':
            answers = AnswerQuestion.objects.all()
        else:
            try:
                answers = AnswerQuestion.objects.filter(poll_id=pk).all()
            except Exception as er:
                return Response({'error': '{}'.format(er)}, status=HTTPStatus.BAD_REQUEST)
        serialized_answer = AnswerSerializer(answers, many=True)
        return Response({'result': serialized_answer.data}, status=HTTPStatus.OK)

    def post(self, request, format=None):
        try:
            serialized_answer = AnswerSerializer(request.data)
            if serialized_answer.is_valid:
                validated_data = request.data
                # if not request.user:
                #     request.user = user.User.get_user_by_email('ano@nymo.us')

                validated_data['user'] = request.user
                new_answer = serialized_answer.create(validated_data)
                if new_answer.event == 'finished':
                    counter = Poll.objects.get(poll_id=request.data['poll_id'])
                    counter.count_answers = counter.count_answers + 1
                    counter.save()
                new_answer.save()

        except Exception as er:
            return Response({'error': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The answer has been created'}, status=HTTPStatus.OK)


class AnswerCollection(APIView):

    def get(self, request, pk, format=None):
        try:
            answer = AnswerQuestion.objects.get(id=pk)
        except AnswerQuestion.DoesNotExist:
            return Response({'result': 'This answer is not exist'}, status=HTTPStatus.NOT_FOUND)


        serialized_answer = AnswerSerializer(answer, many=False)
        return Response({'result': serialized_answer.data}, status=HTTPStatus.OK)

    # def put(self, request, pk, format=None):
    #     try:
    #         poll_serializer = RollSerializer(request.data)
    #         if poll_serializer.is_valid:
    #             new_poll = poll_serializer.create(request.user, request.data)
    #             new_poll.save()
    #     except Exception as er:
    #         return Response({'error': str(er)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    #     return Response({'result': 'The poll has been created'}, status=HTTPStatus.OK)

    def delete(self, request, pk, format=None):
        try:
            polls_count = AnswerQuestion.objects.filter(poll_id=pk).delete()
            if polls_count == 0:
                return Response({'result': 'This answer is not found'}, status=HTTPStatus.NOT_FOUND)
        except Exception as er:
            return Response({'error': str(er)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The answer has been deleted'}, status=HTTPStatus.OK)


class UserAnswerCollectionSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None, format=None):

        try:
            if pk:
                answers = UserAnswerQuestion.objects.filter(poll_id=pk).all()
            else:
                answers = UserAnswerQuestion.objects.all()
        except Exception as er:
            return Response({'error': '{}'.format(er)}, status=HTTPStatus.BAD_REQUEST)
        serialized_answer = UserAnswerSerializer(answers, many=True)
        return Response({'result': serialized_answer.data}, status=HTTPStatus.OK)

    def post(self, request, pk=None, format=None):
        try:
            if 'video_answer' not in request.data:
                request.data['video_answer'] = None
            serialized_answer = UserAnswerSerializer(request.data)
            if serialized_answer.is_valid:
                validated_data = request.data

                new_answer = serialized_answer.create(validated_data)

                if new_answer.event == 'finished':
                    poll = Poll.objects.get(poll_id=request.data['poll_id'])
                    poll.count_answers = poll.count_answers + 1

                    # survey_passing_event_finish(
                    #     poll=poll,
                    #     request=request,
                    #     survey_passing_id=request.data['survey_id']
                    # )

                    survey_passings = SurveyPassing.objects.filter(id=request.data['survey_id'])
                    serialized_survey_passings = SurveyPassingSerializer(survey_passings, many=True)

                    logging.info(f'Get data: {serialized_survey_passings.data}')

                    # try:
                    #     array = serialized_survey_passings.data[0]
                    #     external_api = PollSettings.objects.get(poll_id=request.data['poll_id'])
                    #     if external_api.externalapi and external_api.externalapiparams:
                    #         externalAPI(
                    #             array,
                    #             external_api.externalapi,
                    #             external_api.externalapiparams
                    #         )
                    # except Exception as er:
                    #     return Response({'error answer': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

                    poll.save()

                new_answer.save()
                survey_status = SurveyPassing.objects.get(id=request.data['survey_id'])
                if request.data['event'] != 'points':
                    survey_status.status = request.data['event']
                survey_status.save()
        except Exception as er:
            return Response({'error': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The answer has been created'}, status=HTTPStatus.OK)


class UserAnswerBySurveyCollectionSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None, format=None):

        try:
            if pk:
                answers = UserAnswerQuestion.objects.filter(survey_id=pk).all()
            else:
                answers = UserAnswerQuestion.objects.all()
        except Exception as er:
            return Response({'error': '{}'.format(er)}, status=HTTPStatus.BAD_REQUEST)
        serialized_answer = UserAnswerSerializer(answers, many=True)
        return Response({'result': serialized_answer.data}, status=HTTPStatus.OK)

    def post(self, request, pk=None, format=None):
        try:
            if 'video_answer' not in request.data:
                request.data['video_answer'] = None
            serialized_answer = UserAnswerSerializer(request.data)
            if serialized_answer.is_valid:
                validated_data = request.data
                # if not request.user or not request.user.is_staff:
                #     request.user = user.User.get_user_by_email('ano@nymo.us')

                validated_data['user'] = request.user
                new_answer = serialized_answer.create(validated_data)
                if new_answer.event == 'finished':
                    counter = Poll.objects.get(poll_id=request.data['poll_id'])
                    counter.count_answers = counter.count_answers + 1
                    counter.save()
                new_answer.save()
                survey_status = SurveyPassing.objects.get(id=request.data['survey_id'])
                survey_status.status = request.data['event']
                survey_status.save()
        except Exception as er:
            return Response({'error': f'{er}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return Response({'result': 'The answer has been created'}, status=HTTPStatus.OK)
