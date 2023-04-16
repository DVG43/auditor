from rest_framework import serializers

from testform.models import TestForm


class TestFormSerializer(serializers.ModelSerializer):
    """
    TestForm model serializer implementation.
    """

    class Meta:
        model = TestForm
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'last_modified_user',
            'last_modified_date',
            'delete_id',
            'deleted_since',
            'owner'
        ]

    def __init__(self, *args, **kwargs):
        super(TestFormSerializer, self).__init__(*args, **kwargs)
        self.owner = None
        if 'request' in self.context:
            self.owner = self.context.get('request').user

    def to_representation(self, instance):
        response = {
            'id': instance.id,
            'author': instance.owner.email,
            'name': instance.name,
            'time_to_answer': instance.time_to_answer,
        }
        return response
