from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.exceptions import ValidationError

from accounts.models import User
from common.models import UserColumn
from common.serializers import PpmDocSerializer
from projects.models import Project
from table.models import DefaultTableModel, DefaultTableFrame
from rest_framework import serializers


class DefaultTableSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True, required=False)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)
    document_logo_url = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = DefaultTableModel
        fields = "__all__"

    def get_model(self, obj):
        return 'table'


class DefaultTableFrameSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()

    class Meta:
        model = DefaultTableFrame
        fields = "__all__"

    def get_model(self, obj):
        return 'Tableframe'


class UserColumnSerializer(WritableNestedModelSerializer, PpmDocSerializer):
    column_id = serializers.IntegerField(source='id', read_only=True)
    column_type = serializers.CharField(max_length=11)
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True, required=False)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)
    host_document_id = serializers.IntegerField(required=False)

    class Meta:
        model = UserColumn
        fields = [
            'column_id',
            'column_name',
            'column_type',
            'choices',
            'host_project',
            'owner',
            'host_document_id'
        ]

    def run_validation(self, data=None):
        print(data)
        userfield_types = dict(UserColumn.USERCOLUMN_TYPES)
        if 'column_type' in data and data['column_type'] not in userfield_types:
            raise ValidationError({
                'error': {
                    'msg': 'wrong columnType',
                    'choices': userfield_types
                }})
        return super().run_validation(data)
