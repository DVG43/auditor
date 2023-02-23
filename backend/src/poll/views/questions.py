from http import HTTPStatus

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from poll.query import get_or_404
from poll.models.poll import Poll
from poll.models.questions import ManyFromListQuestion, YesNoQuestion, RatingQuestion, MediaQuestion, \
    TextQuestion, DivisionQuestion, FinalQuestion, YesNoAnswers, HeadingQuestion, FreeAnswer, TagsFreeAnswer, \
    ItemTagsFreeAnswer, ItemsFreeAnswer
from poll.permissions import check_question_permission
from poll.serializers.questions import ManyFromListQuestionSerializer, YesNoQuestionSerializer, \
    RatingQuestionSerializer, MediaQuestionSerializer, TextQuestionSerializer, DivisionQuestionSerializer, \
    FinalQuestionSerializer, YesNoAnswersSerializer, HeadingQuestionSerializer, FreeAnswerSerializer, \
    TagsFreeAnswerSerializer, ItemTagsFreeAnswerSerializer
from poll.utils import QUESTION_SERIALIZERS_V1, QUESTION_MODELS


class QuestionCollection(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super(QuestionCollection, self).get_permissions()

    def get(self, request, pk, question_type=None, format=None):
        """
        Get question
        """
        if not question_type:
            try:
                division = DivisionQuestion.objects.filter(poll_id=pk).all()
                division_questions = DivisionQuestionSerializer(division, many=True)

                yes_no = YesNoQuestion.objects.filter(poll_id=pk).all()
                yesno_questions = YesNoQuestionSerializer(yes_no, many=True)

                manyfromlist = ManyFromListQuestion.objects.filter(poll_id=pk).all()
                manyfromlist_questions = ManyFromListQuestionSerializer(manyfromlist, many=True)

                text = TextQuestion.objects.filter(poll_id=pk).all()
                text_questions = TextQuestionSerializer(text, many=True)

                rating = RatingQuestion.objects.filter(poll_id=pk).all()
                rating_questions = RatingQuestionSerializer(rating, many=True)

                media = MediaQuestion.objects.filter(poll_id=pk).all()
                media_questions = MediaQuestionSerializer(media, many=True)

                final = FinalQuestion.objects.filter(poll_id=pk).all()
                final_questions = FinalQuestionSerializer(final, many=True)

                heading = HeadingQuestion.objects.filter(poll_id=pk).all()
                heading_question = HeadingQuestionSerializer(heading, many=True)

                free_answer = FreeAnswer.objects.filter(poll_id=pk).all()
                free_answer_serializer = FreeAnswerSerializer(free_answer, many=True)

                return Response(
                    {'result': (division_questions.data,
                                yesno_questions.data,
                                manyfromlist_questions.data,
                                text_questions.data,
                                rating_questions.data,
                                media_questions.data,
                                final_questions.data,
                                heading_question.data,
                                free_answer_serializer.data)}, status=HTTPStatus.OK)
            except Exception as er:
                return Response(f'{er}')
        else:
            try:

                if not (question_type and question_type in QUESTION_SERIALIZERS_V1):
                    return Response({'error': 'Question type is not found'}, status=HTTPStatus.BAD_REQUEST)

                model = QUESTION_MODELS[question_type]
                serializer = QUESTION_SERIALIZERS_V1[question_type]

                question = get_or_404(model, question_id=pk)
                serialized_questions = serializer(question)

                if serialized_questions:
                    return Response({'result': serialized_questions.data}, status=HTTPStatus.OK)
                else:
                    raise Exception('Bad request')

            except ManyFromListQuestion.DoesNotExist or YesNoQuestion.DoesNotExist or RatingQuestion.DoesNotExist \
                   or ManyFromListQuestion.DoesNotExist or TextQuestion.DoesNotExist or MediaQuestion.DoesNotExist \
                   or FinalQuestion.DoesNotExist or HeadingQuestion.DoesNotExist:
                return Response({'result': 'Not found'}, status=HTTPStatus.NOT_FOUND)
            except Exception as er:
                return Response({'error': '{}'.format(er)}, status=HTTPStatus.BAD_REQUEST)

    def post(self, request, pk):
        poll = Poll.objects.get(poll_id=pk)
        check_question_permission(poll, request)

        # bulk create
        final_result = []
        for data in request.data if isinstance(request.data, list) else [request.data]:
            question_type = data.get('question_type', None)

            if not (question_type and question_type in QUESTION_SERIALIZERS_V1):
                return Response({'error': 'Question type is not found'}, status=HTTPStatus.BAD_REQUEST)

            data['poll_id'] = poll.pk
            question_serializer = QUESTION_SERIALIZERS_V1[question_type]
            serializer = question_serializer(data)

            if serializer.is_valid:
                new_question = serializer.create(data)
                new_question.save()
            else:
                Response({'error': 'Question is not valid'}, status=HTTPStatus.BAD_REQUEST)

            result = serializer.data
            result['question_id'] = new_question.question_id
            poll.normalize_questions_order_id()
            final_result.append(result)

        result = final_result[0] if isinstance(request.data, dict) else final_result
        return Response({'result': result}, status=HTTPStatus.OK)

    def delete(self, request, pk, question_type, format=None):
        if not (question_type and question_type in QUESTION_SERIALIZERS_V1):
            return Response({'error': 'Question type is not found'}, status=HTTPStatus.BAD_REQUEST)

        model = QUESTION_MODELS[question_type]
        question = model.objects.filter(question_id=pk)
        poll = question.first().poll
        check_question_permission(poll, request)
        count = question.delete()
        if count == 0:
            return Response({'result': 'This question is not found'}, status=HTTPStatus.NOT_FOUND)

        poll.normalize_questions_order_id()
        return Response({'result': 'The question has been deleted'}, status=HTTPStatus.OK)

    def put(self, request, pk, question_type, format=None):
        if not (question_type and question_type in QUESTION_SERIALIZERS_V1):
            return Response({'error': 'Question type is not found'}, status=HTTPStatus.BAD_REQUEST)

        model = QUESTION_MODELS[question_type]
        serializer = QUESTION_SERIALIZERS_V1[question_type]

        question = get_or_404(model, question_id=pk)
        poll = question.poll
        check_question_permission(poll, request)
        edit_question = serializer().update(question, request.data)
        serialized_questions = serializer(edit_question)
        poll.normalize_questions_order_id()
        if edit_question:
            question.poll.normalize_questions_order_id()
            return Response({'result': serialized_questions.data}, status=HTTPStatus.OK)
        else:
            raise Exception('Bad request')


class YesNoAnswersView(generics.RetrieveUpdateDestroyAPIView):
    queryset = YesNoAnswers.objects.all()
    serializer_class = YesNoAnswersSerializer


class YesNoAnswersCreateAPIView(APIView):
    queryset = YesNoAnswers.objects.all()
    serializer_class = YesNoAnswersSerializer

    def post(self, request):
        question_id = request.data.pop('question_id')
        question = YesNoQuestion.objects.get(question_id=question_id)
        serializer = YesNoAnswersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question.yes_no_answers.add(serializer.save())
        return Response(serializer.data)


class ManyFromListQuestionCaptionView(APIView):

    def get(self, request, pk):
        many_from_list_question = list(
            ManyFromListQuestion.objects.filter(poll_id=pk).values('caption', 'question_id')
        )
        return Response({'result': many_from_list_question}, status=HTTPStatus.OK)


class TagFreeAnswer(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = TagsFreeAnswer.objects.all()
    serializer_class = TagsFreeAnswerSerializer

    def post(self, request, pk):
        question = FreeAnswer.objects.get(question_id=pk)
        serializer = TagsFreeAnswerSerializer(data=request.data, context={'question': question})
        serializer.is_valid(raise_exception=True)
        question.tags.add(serializer.save())
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        super(TagFreeAnswer, self).delete(self, request, *args, **kwargs)
        return Response({'result': 'The tag has been deleted'}, status=HTTPStatus.OK)


class ItemTagFreeAnswer(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = ItemTagsFreeAnswer.objects.all()
    serializer_class = ItemTagsFreeAnswerSerializer

    def post(self, request, pk):
        item = ItemsFreeAnswer.objects.get(item_question_id=pk)
        serializer = ItemTagsFreeAnswerSerializer(data=request.data, context={'item': item})
        serializer.is_valid(raise_exception=True)
        item.tags.add(serializer.save())
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        super(ItemTagFreeAnswer, self).delete(self, request, *args, **kwargs)
        return Response({'result': 'The tag has been deleted'}, status=HTTPStatus.OK)
