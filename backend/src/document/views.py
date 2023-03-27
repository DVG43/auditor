from json import loads
from accounts.permissions import IsActivated
from common.permissions import IsOwner, IsOwnerOrIsInvited
from django.shortcuts import get_object_or_404
from document.models import Document
from document.serializers import (
    DocumentLogoSerializer,
    ProjectSerializer,
    DocumentSerializer,
    ImageGenerationSerializer,
    AudioGenerationSerializer,
)
from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from projects.models import Project
from settings import MEDIA_URL
from rest_framework import views
from document import utils


class ChangeDocumentLogoView(generics.UpdateAPIView):
    serializer_class = DocumentLogoSerializer
    permission_classes = [IsAuthenticated, IsOwner]
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
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]

    def get_queryset(self):
        document = Document.objects.select_related('host_project').all()
        return document

    def get_serializer_class(self):
        return DocumentSerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]

    def get_queryset(self):
        project = Project.objects.prefetch_related('documents').all()
        return project

    def get_serializer_class(self):
        return ProjectSerializer


class ImageGeneration(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = ImageGenerationSerializer

    def post(self, request, *args, **kwargs):
        """
        Создает изображения по описанию prompt. Изображения сохраняютя в PATH_IMAGES.\n
        param:\n
            prompt (str): описание желаемого изображения, максимальная длина 1000 символов\n
            n (int): количество генерируемых изображений на основе описания prompt, от 1 до 10\n
            size (int): размер генерируемых изображений: 0, 1 или 2
        """
        # проверка валидности полей
        serializer = ImageGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # извлечение знач переменных
        prompt = request.data.get('prompt')
        n = int(request.data.get('n'))
        size = int(request.data.get('size'))

        # формирование изображений
        fnames = utils.image_generator(prompt, n, size)
        answer = dict()
        web_server = request.META['HTTP_HOST'].split(':')[0]
        for i in range(len(fnames)):
            answer[i] = f"http://{web_server}{MEDIA_URL}images/{fnames[i]}"

        return Response(answer)

def get_text(lst, txt = ''):
  for elm in lst:
    if 'children' in elm.keys():
      txt += get_text(elm['children'])
    else:
      txt += elm['text'] + ' ' if elm['text'] != '/' else ''
  return txt

class Text2Speech(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = AudioGenerationSerializer

    def post(self, request, *args, **kwargs):
        """
        Генерирует речь из текста документа и сохраняет её в файл формата mp3 в {MEDIA_URL}audio/\n
        param:\n
            id (int): id документа
            lang (str): язык, приемлемые значения ['ru-RU', 'en-US', 'kk-KK', 'de-DE', 'uz-UZ'], по умолчанию ru-RU
            voice (str): предпочтительный голос синтеза речи из списка ['alena', 'filipp', 'ermil', 'jane', 'madirus', 'omazh', 'zahar', 'oksana', 'nigora', 'lea', 'amira', 'madi'], значение по умолчанию: Оксана
            speed (str): темп (скорость) синтезированной речи, скорость речи задается десятичным числом в диапазоне от 0,1 до 3,0. Где:
                3.0 — Самая высокая скорость.
                1.0 (по умолчанию) — средняя скорость речи человека.
                0,1 — самая низкая скорость речи.
        """
        # проверка валидности полей
        serializer = AudioGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content = get_object_or_404(Document, pk=kwargs['pk']).content.replace("null", '""')
        text = get_text(loads(content)["root"]["children"])

        # извлечение знач переменных
        lang = request.data.get('lang')
        voice = request.data.get('voice')
        speed = request.data.get('speed')

        # формируем речь и возвращаем ссылку на файл
        fname = utils.text2speech(text, lang, voice, speed)
        answer = f"https://{request.META['HTTP_HOST']}{MEDIA_URL}audio/{fname}"
        return Response(answer)