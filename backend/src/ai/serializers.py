
from rest_framework import serializers


class ThemeToTextSerializer(serializers.Serializer):
    """ Ввод текста темы для генерации абзаца """
    source = serializers.CharField()
    tone = serializers.ChoiceField(choices={
            "Grateful",      # Благодарный
            "Excited",       # Восхищенный
            "Rude",          # Грубый
            "Sad",           # Грустный
            "Informative",   # Информативный
            "Witty",         # Остроумный
            "Negative",      # Негативный
            "Neutral",       # Естественный
            "Positive",      # Позитивный
            "Professional",  # Формальный
            "Convincing",    # Убедительный
            "Engaging",      # Развлекательный
            "Humorous",      # Юмористический
        },
        required=False,
        allow_null=True)
    language = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)


class TextRephraseSerializer(serializers.Serializer):
    """ Ввод текста для перефразирования """
    source = serializers.CharField()


class TextShorterSerializer(serializers.Serializer):
    """ Ввод текста для сокращения """
    source = serializers.CharField()


class TextContinueSerializer(serializers.Serializer):
    """ Ввод текста для увеличения объема текста """
    source = serializers.CharField()


class QueryAiSerializer(serializers.Serializer):
    """ Ввод произвольного запроса к AI с опциональным контекстом """
    source = serializers.CharField()
    context = serializers.CharField(required=False)



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










