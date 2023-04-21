
from rest_framework import serializers


class QueryAiSerializer(serializers.Serializer):
    """ Ввод произвольного запроса к AI с опциональным контекстом """
    source = serializers.CharField(allow_blank=True)
    context = serializers.CharField(required=False, allow_blank=True)


class StandardGenerationSerializer(serializers.Serializer):
    """ Ввод стандартной команды для AI генерации текста """
    context = serializers.CharField()
    command = serializers.ChoiceField(choices={
            "Сократить текст",
            "Расширить текст",
            "Продолжить писать",
            "Изменить тон на обычный",
            "Изменить тон на формальный",
            "Подвести итог",
            "Объяснить это",
        },
        required=True,
        allow_null=False)










