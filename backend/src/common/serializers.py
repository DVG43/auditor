from django.contrib.contenttypes.models import ContentType
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import User
from common.models import PERMS, UserColumn, UserCell, UserChoice, UsercellImage, StandardIcon
from objectpermissions.models import UserPermission
from projects.models import Project


class PpmDocSerializer(serializers.ModelSerializer):
    invites = serializers.SerializerMethodField()
    perms = serializers.SerializerMethodField()
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        read_only_fields = [
            'created_at',
            'last_modified_user',
            'last_modified_date',
            'delete_id',
            'deleted_since'
        ]

    def create(self, validated_data):
        print(validated_data)
        if 'owner' not in validated_data:
            if ('request' in self.context and
            'owner' in self.context['request'].data.keys()):
                validated_data.update({
                    'owner': self.context['request'].data.get('owner')
                })
            elif 'request' in self.context:
                validated_data.update(
                    {'owner': self.context['request'].user})
            elif 'user' in self.context:
                validated_data.update(
                    {'owner': self.context['user']})
        instance = super().create(validated_data)

        if hasattr(instance, "perms"):
            instance.owner.grant_object_perm(instance, 'own')
        return instance

    def get_invites(self, obj):
        user = self.context['request'].user
        if obj.owner != user:
            if user.has_object_perm(obj, ['read']):
                return "read"
            elif user.has_object_perm(obj, ['edit']):
                return "edit"
        model_name = obj.__class__.__name__.lower()
        ct = ContentType.objects.get(model=model_name)
        shared_docs = UserPermission.objects \
            .filter(object_id=obj.id) \
            .filter(content_type_id=ct) \
            .exclude(user_id=obj.owner.pkid)\
            .exclude(user_id__is_active=False)
        response_data = {}
        if shared_docs:
            for up in shared_docs:
                # Конвертируем разрешения в строковый вид
                sh_perm_str = PERMS.as_string_list(up.permission)
                response_data.update({up.user.email: sh_perm_str})
        return response_data

    def get_perms(self, obj):
        user = self.context['request'].user
        perms = user.get_object_perm_as_str_list(obj)
        return perms[0] if len(perms) == 1 else perms


class UserChoiceSerializer(PpmDocSerializer):
    class Meta:
        model = UserChoice
        fields = [
            'id',
            'choice',
            'color'
        ]


class UserColumnSerializer(WritableNestedModelSerializer, PpmDocSerializer):
    column_id = serializers.IntegerField(source='id', read_only=True)
    choices = serializers.SerializerMethodField()
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

    def get_choices(self, obj):
        return UserChoiceSerializer(many=True, required=False)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChoice
        fields = ['choice']


class UsercellImageSerializer(PpmDocSerializer):
    host_usercell = serializers.PrimaryKeyRelatedField(
        queryset=UserCell.objects.all(), write_only=True
    )

    class Meta:
        model = UsercellImage
        fields = ['id', 'file', 'host_usercell']


class UserCellSerializer(WritableNestedModelSerializer, PpmDocSerializer):
    column_id = serializers.IntegerField(source='host_usercolumn.id',
                                         read_only=True)
    cell_id = serializers.IntegerField(
        source='id', read_only=True, required=False)
    column_name = serializers.StringRelatedField(
        source='host_usercolumn.column_name', read_only=True)
    column_type = serializers.StringRelatedField(
        source='host_usercolumn.column_type', read_only=True)
    host_usercolumn = serializers.PrimaryKeyRelatedField(
        queryset=UserColumn.objects.all(), write_only=True
    )
    choices_id = serializers.ListSerializer(
        child=serializers.IntegerField()
    )
    choice_id = serializers.PrimaryKeyRelatedField(
        queryset=UserChoice.objects.all()
    )
    images = UsercellImageSerializer(many=True)

    class Meta:
        model = UserCell
        fields = [
            'cell_id', 'cell_content', 'choice_id', 'images',
            'id', 'host_usercolumn',
            'column_id', 'column_name', 'column_type',
            'choices_id'
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


class CalendarDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    model = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    date = serializers.DateField(read_only=True)


class CalendarSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
    project_name = serializers.CharField(required=True)
    documents = CalendarDocumentSerializer(many=True, read_only=True)


class StandardIconSerializer(serializers.ModelSerializer):
    """Serializer to StandardIcon model."""
    class Meta:
        model = StandardIcon
        fields = ['id', 'icon_image', ]
