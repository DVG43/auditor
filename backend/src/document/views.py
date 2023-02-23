from accounts.permissions import IsActivated
from common.permissions import IsOwner, IsOwnerOrIsInvited
from django.shortcuts import get_object_or_404
from document.models import Document
from document.serializers import DocumentLogoSerializer, ProjectSerializer, DocumentSerializer, \
    TextGenerationSerializer, TextRephraseSerializer
from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project
from settings import MEDIA_URL
from rest_framework import views
from document import utils
from document.ai_translator import AiTranslator
import openai
import settings

openai.api_key = settings.api_key


class ChangeDocumentLogoView(generics.UpdateAPIView):
    serializer_class = DocumentLogoSerializer
    permission_classes = [IsAuthenticated, IsActivated, IsOwner]
    queryset = Document.objects.all()

    def patch(self, request, *args, **kwargs):
        document = get_object_or_404(Document, pk=kwargs['doc_pk'])
        if request.user != document.owner:
            raise PermissionDenied({'error': 'You don`t have access to this object'})
        document.document_logo = request.data['document_logo']
        document.save()
        resp = f"https://{request.META['HTTP_HOST']}" \
               f"{MEDIA_URL}" \
               f"{document.document_logo}"
        return Response(resp)


class DicumentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsActivated, IsOwnerOrIsInvited]

    def get_queryset(self):
        document = Document.objects.select_related('host_project').all()
        return document

    def get_serializer_class(self):
        return DocumentSerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsActivated, IsOwnerOrIsInvited]

    def get_queryset(self):
        project = Project.objects.prefetch_related('documents').all()
        return project

    def get_serializer_class(self):
        return ProjectSerializer


class TextGeneration(views.APIView):
    permission_classes = [IsAuthenticated, IsActivated, IsOwnerOrIsInvited]
    serializer_class = TextGenerationSerializer

    def post(self, request, *args, **kwargs):
        # проверка валидности полей
        if request.data.get('tone') == "null":
            request.data['tone'] = None
        serializer = TextGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # извлечение знач переменных
        source = request.data.get('source')
        language = request.data.get('language')
        tone = request.data.get('tone')
        max_tokens = 1500
        # if request.data.get('max_tokens'):
        #     max_tokens = request.data.get('max_tokens')

        # формирование ответа
        model = "text-davinci-003"
        prompt = AiTranslator.theme_to_paragraph_prompt(theme=source, len_words=85, lang=language, tone=tone)
        result = utils.text_generator(prompt, model, max_tokens)
        result.choices[0].text = AiTranslator.theme_to_paragraph_postprocess(result.choices[0].text)
        return Response(result, status=200)


class TextRephrase(views.APIView):
    permission_classes = [IsAuthenticated, IsActivated, IsOwnerOrIsInvited]
    serializer_class = TextRephraseSerializer

    def post(self, request, *args, **kwargs):
        # проверка валидности полей
        serializer = TextRephraseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # извлечение знач переменных
        source = request.data.get('source')
        max_tokens = 500
        # if request.data.get('max_tokens'):
        #     max_tokens = request.data.get('max_tokens')

        # формирование ответа
        model = "text-davinci-003"
        prompt = AiTranslator.rephrase_prompt(source),
        result = utils.text_generator(prompt, model, max_tokens)
        if result.choices[0].text != "":
            result.choices[0].text = AiTranslator.rephrase_postprocess(result.choices[0].text)
        return Response(result, status=200)
