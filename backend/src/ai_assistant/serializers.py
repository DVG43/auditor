from common.serializers import PpmDocSerializer
from projects.serializers import FilteredListSerializer
from ai_assistant.models import AiAssistant


class AiAssistantSerializer(PpmDocSerializer):

    class Meta:
        model = AiAssistant
        list_serializer_class = FilteredListSerializer
        fields = '__all__'
