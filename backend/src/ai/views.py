from accounts.permissions import IsActivated
from common.permissions import IsOwner, IsOwnerOrIsInvited

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views

from settings import DEBUG

from . import serializers
from . import ai


class ThemeToText(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = serializers.ThemeToTextSerializer

    def post(self, request, *args, **kwargs):
        """
        Генерирует абзац текста согласно теме.

        Пример ответа:
        ```json
        {
            "payload": "... сгенерированный текст ...",
            "error": null
        }
        ```

        - В случае успешной генерации `payload` содержит результат, а `error=null`.
        - В случае ошибки `payload=null`, а `error` содержит описание ошибки без подробностей, которое можно безопасно показать пользователю.
        """
        # 1. Проверка валидности полей
        if request.data.get('tone') == "null":
            request.data['tone'] = None
        serializer = serializers.ThemeToTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Извлечение значений переменных из HTTP запроса
        source = request.data.get('source')
        language = request.data.get('language')
        tone = request.data.get('tone')
        keywords = request.data.get('keywords')

        # 3. Получение ответа от AI
        result = ai.theme_to_text(theme=source, tone=tone, lang=language,
            keywords=keywords, include_debug=DEBUG)

        return Response(result, status=200)


class TextRephrase(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = serializers.TextRephraseSerializer

    def post(self, request, *args, **kwargs):
        """
        Возвращает несколько вариантов такого же по смыслу текста, но другими словами.

        Пример ответа:
        ```json
        {
            "payload": [
                "Вариант первый",
                "Вариант второй",
                ...
            ],
            "error": null
        }
        ```
        """
        # 1. Проверка валидности полей
        serializer = serializers.TextRephraseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Извлечение значений переменных из HTTP запроса
        source = request.data.get('source')

        # 3. Получение ответа от AI
        result = ai.text_rephrase(source, include_debug=DEBUG)

        return Response(result, status=200)


class TextShorter(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = serializers.TextShorterSerializer

    def post(self, request, *args, **kwargs):
        """
        Делает текст короче, не меняя смысл.

        Пример ответа:
        ```json
        {
            "payload": "... сгенерированный текст ...",
            "error": null
        }
        ```
        """
        serializer = serializers.TextShorterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source = request.data.get('source')

        result = ai.text_shorter(source, include_debug=DEBUG)
        return Response(result, status=200)


class TextContinue(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = serializers.TextContinueSerializer

    def post(self, request, *args, **kwargs):
        """
        Генерирует продолжение для заданного текста.

        Пример ответа:
        ```json
        {
            "payload": "... сгенерированный текст ...",
            "error": null
        }
        ```
        """
        serializer = serializers.TextContinueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source = request.data.get('source')

        result = ai.text_continue(source, include_debug=DEBUG)
        return Response(result, status=200)


class QueryAi(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = serializers.QueryAiSerializer

    def post(self, request, *args, **kwargs):
        """
        Генерирует текст согласно запросу пользователя. Можно
        использовать дополнительный контекст.

        Пример ответа:
        ```json
        {
            "payload": "... ответ ИИ ...",
            "error": null
        }
        ```
        """
        serializer = serializers.QueryAiSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source = request.data.get('source')
        context = request.data.get('context')

        result = ai.query_ai(source, context, include_debug=DEBUG)
        return Response(result, status=200)



class StandardGeneration(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrIsInvited]
    serializer_class = serializers.StandardGenerationSerializer

    def post(self, request, *args, **kwargs):
        """
        Генерирует текст согласно одной из стандартного набора команд.

        Пример ответа:
        ```json
        {
            "payload": "... ответ ИИ ...",
            "error": null
        }
        ```
        """
        serializer = serializers.StandardGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        context = request.data.get('context')
        command = request.data.get('command')

        result = ai.standard_generation(command, context,
            include_debug=DEBUG)
        return Response(result, status=200)
