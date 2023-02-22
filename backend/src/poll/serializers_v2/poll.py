from rest_framework.serializers import ModelSerializer
from poll.models.poll import Poll


class PollSerializer(ModelSerializer):
    class Meta:
        model = Poll
        fields = [
            'poll_id',
            'user',
            'title',
            'image',
            'test_mode_global',
            'count_answers',
            'last_open',
        ]
