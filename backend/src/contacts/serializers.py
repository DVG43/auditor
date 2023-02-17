from pprint import pprint

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from common.serializers import PpmDocSerializer
from contacts.models import Contact, Position, Department


class PositionSerializer(PpmDocSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'tag_color']


class DepartmentSerializer(PpmDocSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'tag_color']


class ContactSerializer(WritableNestedModelSerializer, PpmDocSerializer):
    department = DepartmentSerializer(required=False, allow_null=True)
    position = PositionSerializer(required=False, allow_null=True)
    in_projects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'email',
                  'department',
                  'position',
                  'in_projects']


class ContactSearchSerializer(serializers.Serializer):
    email = serializers.CharField()
    name = serializers.CharField()


class ContactSearchSerializerRequest(serializers.Serializer):
    email = serializers.CharField()


class ContactsDeleteListRequest(serializers.Serializer):
    contacts = serializers.ListField(child=serializers.IntegerField())
