from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from poll.query import get_or_404
from poll.utils import QUESTION_MODELS, ITEM_MODELS, ITEM_SERIALIZERS_V2, ATTACHED_TYPE_SERIALIZERS_V2, \
    ATTACHED_TYPE_MODELS


class CreateSubQuestionObjects(generics.CreateAPIView):
    serializers_classes = []
    models_classes = []
    question = None

    def get_question_type(self):
        question_type = self.kwargs.get('question_type')
        if not question_type or question_type not in self.models_classes:
            raise NotFound('question type is not found')
        return question_type

    def get_question(self):
        # для многоразового использования question объекта без лишних sql запросов
        if not self.question:
            question_type = self.kwargs.get('question_type')
            question = get_or_404(QUESTION_MODELS[question_type], pk=self.kwargs.get('pk'))
            self.question = question
        return self.question

    def get_serializer_context(self):
        return {
            'question': self.get_question()
        }

    def get_serializer_class(self):
        question_type = self.get_question_type()
        return self.serializers_classes[question_type]

    def create(self, request, *args, **kwargs):
        if type(request.data) is list:
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UpdateSubQuestionObject(generics.UpdateAPIView,
                              generics.DestroyAPIView):
    models_classes = []
    serializers_classes = []

    def get_question_type(self):
        question_type = self.kwargs.get('question_type')
        if not question_type or question_type not in self.models_classes:
            raise NotFound('question type is not found')
        return question_type

    def get_object(self):
        question_type = self.get_question_type()
        model = self.models_classes[question_type]
        obj = get_or_404(model, pk=self.kwargs.get('pk'))
        return obj

    def get_serializer_class(self):
        question_type = self.get_question_type()
        return self.serializers_classes[question_type]

    def destroy(self, request, *args, **kwargs):
        super(UpdateSubQuestionObject, self).destroy(request, *args, **kwargs)
        return Response({'result': 'ok'})


class ItemCreateViewSet(CreateSubQuestionObjects):
    permission_classes = [IsAuthenticated]
    serializers_classes = ITEM_SERIALIZERS_V2
    models_classes = ITEM_MODELS


class ItemViewSet(UpdateSubQuestionObject):
    permission_classes = [IsAuthenticated]
    serializers_classes = ITEM_SERIALIZERS_V2
    models_classes = ITEM_MODELS


class AttachedTypeCreateViewSet(CreateSubQuestionObjects):
    permission_classes = [IsAuthenticated]
    serializers_classes = ATTACHED_TYPE_SERIALIZERS_V2
    models_classes = ATTACHED_TYPE_MODELS


class AttachedTypeViewSet(UpdateSubQuestionObject):
    permission_classes = [IsAuthenticated]
    serializers_classes = ATTACHED_TYPE_SERIALIZERS_V2
    models_classes = ATTACHED_TYPE_MODELS
