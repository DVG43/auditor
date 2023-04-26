import json

from accounts.permissions import IsActivated
from common.permissions import IsOwner, IsOwnerOrIsInvited

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views

from django.http import StreamingHttpResponse

from settings import DEBUG

from . import serializers
from . import ai


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


class StreamTest(views.APIView):
    serializer_class = serializers.QueryAiSerializer

    def get(self, request, *args, **kwargs):
        """
        Эндпоинт для тестирования потоковой передачи данных (stream).
        """
        def generate_stream():
            import time
            time_0 = time.time()
            yield f'data: {{"payload": "{time.time() - time_0:.3f}s"}}\n\n'
            for i in range(6000):
                time.sleep(0.01)
                yield f'data: {{"payload": "{time.time() - time_0:.3f}s"}}\n\n'
        return StreamingHttpResponse(generate_stream(), content_type='text/event-stream')


    def post(self, request, *args, **kwargs):
        """
        Эндпоинт для тестирования потоковой передачи данных (stream).
        """
        serializer = serializers.QueryAiSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source = request.data.get('source')
        context = request.data.get('context')

        def generate_stream():
            import json
            import time

            time_0 = time.time()
            data = json.dumps({
                'payload': f'{time.time() - time_0:.3f}s',
                'source': source,
                'context': context,
            })
            yield f"data: {data}"

            for i in range(20):
                print('stream', i)
                time.sleep(0.5)
                data = json.dumps({
                    'payload': f'+{time.time() - time_0:.3f}s',
                    'source': source,
                    'context': context,
                })
                yield f"data: {data}"

        return StreamingHttpResponse(
            generate_stream(), content_type='text/event-stream')


class QueryAiStream(views.APIView):
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

        streaming_result = ai.query_ai_stream(source, context,
            include_debug=DEBUG)

        json_lines = lambda obj: json.dumps(obj) + '\n'
        streaming_json = map(json_lines, streaming_result)
        return StreamingHttpResponse(streaming_json)


class StandardGenerationStream(views.APIView):
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

        streaming_result = ai.standard_generation_stream(command,
            context, include_debug=DEBUG)

        json_lines = lambda obj: json.dumps(obj) + '\n'
        streaming_json = map(json_lines, streaming_result)
        return StreamingHttpResponse(streaming_json)
