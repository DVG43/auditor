import datetime

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from poll.models.poll import Poll
from poll.models.surveypassing import SurveyPassing
from poll.serializers.answer import UserAnswerSerializer
from poll.utils import QUESTION_SERIALIZERS_V1


class SurveyPassingSerializer(serializers.ModelSerializer):
    poll = serializers.SlugRelatedField(
        required=True,
        queryset=Poll.objects.all(),
        slug_field='id'
     )
    answers = serializers.JSONField(required=True)

    class Meta:
        model = SurveyPassing
        fields = ('poll', 'answers',)
        read_only_fields = ('created_at', )

    def create(self, validated_data):
        return SurveyPassing.objects.create(**validated_data)
