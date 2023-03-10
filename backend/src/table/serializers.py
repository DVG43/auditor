from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.exceptions import ValidationError

from accounts.models import User
from common.models import UserColumn, UserChoice
from common.serializers import PpmDocSerializer
from document.models import Document
from folders.models import Folder
from table.models import DefaultTableModel, DefaultTableFrame, DefaultTableUsercell
from rest_framework import serializers


class DefaultTableFrameSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()

    class Meta:
        model = DefaultTableFrame
        fields = "__all__"

    def get_model(self, obj):
        return 'Tableframe'


class UserColumnSerializer(WritableNestedModelSerializer, PpmDocSerializer):
    column_id = serializers.IntegerField(source='id', required=False)
    column_type = serializers.CharField(max_length=11, required=False)
    host_table = serializers.PrimaryKeyRelatedField(
        queryset=DefaultTableModel.objects.all(), write_only=True, required=False)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = UserColumn
        fields = [
            'column_id',
            'column_name',
            'column_type',
            'owner',
            'host_table'
        ]

    def run_validation(self, data=None):
        userfield_types = dict(UserColumn.USERCOLUMN_TYPES)
        if 'column_type' in data and data['column_type'] not in userfield_types:
            raise ValidationError({
                'error': {
                    'msg': 'wrong columnType',
                    'choices': userfield_types
                }})
        return super().run_validation(data)


class UserChoiceSerializer(PpmDocSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = UserChoice
        fields = [
            'id',
            'choice',
            'color',
            'host_usercolumn',
            'owner'
        ]


class DefaultTableSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()
    host_folder = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all(), write_only=True, required=False)
    host_document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(), write_only=True, required=False)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)
    document_logo_url = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = DefaultTableModel
        fields = "__all__"

    def get_model(self, obj):
        return 'table'


class UserCellSerializer(WritableNestedModelSerializer, PpmDocSerializer):
    cell_id = serializers.IntegerField(
        source='id', read_only=True, required=False)
    host_usercolumn = serializers.PrimaryKeyRelatedField(
        queryset=UserColumn.objects.all(), write_only=True
    )
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = DefaultTableUsercell
        fields = [
            'cell_id', 'cell_content',
            'id', 'host_usercolumn', 'choice_id',
            'choices_id', 'owner', 'frame_id'
        ]

    def update(self, instance, validated_data):
        print(130, 'common UserCellSerializer.update')
        if instance.host_usercolumn.column_type == 'select':
            if 'cell_content' in validated_data:
                validated_data.pop('cell_content')
            if 'choice_id' in validated_data:
                content = validated_data['choice_id'].choice
            else:
                content = ''
            choices_list = instance.host_usercolumn.choices.all().values(
                'choice')
            for choice in choices_list:
                if content in str(choice.values()) or content == '':
                    instance.cell_content = content
                    if content == '':
                        instance.choice_id = None
                    instance.save()
                    break
        return super().update(instance, validated_data)
