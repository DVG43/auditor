from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from poll.query import get_or_404
from poll.models.poll import Poll
from poll.permissions import IsQuestionOwnerOrReadOnly, IsQuestionRedactor
from poll.utils import QUESTION_MODELS, QUESTION_SERIALIZERS_V2


class QuestionCreateView(generics.CreateAPIView):
    permission_classes = [IsQuestionOwnerOrReadOnly | IsQuestionRedactor]

    def get_question_type(self):
        question_type = self.request.data.get('question_type')
        if not question_type or question_type not in QUESTION_MODELS:
            raise NotFound('question type is not found')
        return question_type

    def get_serializer_class(self):
        question_type = self.get_question_type()
        return QUESTION_SERIALIZERS_V2[question_type]

    def post(self, request, *args, **kwargs):
        poll = get_or_404(Poll, pk=self.kwargs.get('pk'))
        request.data['poll_id'] = poll.pk
        resp = self.create(request, *args, **kwargs)
        poll.normalize_questions_order_id()
        return Response(resp.data, status=status.HTTP_201_CREATED)


class QuestionViewSet(generics.UpdateAPIView,
                      generics.DestroyAPIView):
    permission_classes = [IsQuestionOwnerOrReadOnly | IsQuestionRedactor]

    def get_question_type(self):
        question_type = self.kwargs.get('question_type')
        if not question_type or question_type not in QUESTION_MODELS:
            raise NotFound('question type is not found')
        return question_type

    def get_object(self):
        question_type = self.get_question_type()
        model = QUESTION_MODELS[question_type]
        obj = get_or_404(model, pk=self.kwargs.get('pk'))
        return obj

    def get_serializer_class(self):
        question_type = self.get_question_type()
        return QUESTION_SERIALIZERS_V2[question_type]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        poll = instance.poll
        self.perform_destroy(instance)
        poll.normalize_questions_order_id()
        return Response({'result': 'ok'}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        poll = get_or_404(Poll, pk=self.kwargs.get('pk'))
        resp = self.update(request, *args, **kwargs)
        poll.normalize_questions_order_id()
        return Response(resp.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        poll = get_or_404(Poll, pk=self.kwargs.get('pk'))
        resp = self.update(request, *args, **kwargs)
        poll.normalize_questions_order_id()
        return Response(resp.data, status=status.HTTP_200_OK)
