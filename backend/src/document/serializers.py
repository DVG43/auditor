from common.serializers import PpmDocSerializer
from document.models import Document
from rest_framework import serializers
from settings import MEDIA_URL
from projects.models import Project
from folders.models import Folder


class DocumentLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'document_logo'
        ]


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр документов, только parents"""

    def to_representation(self, data):
        data = data.filter(parent=None, deleted_id__isnull=True)
        return super().to_representation(data)


class FilterReviewSerializer(serializers.ListSerializer):
    """Фильтр документов, только children"""

    def to_representation(self, data):
        data = data.filter(deleted_id__isnull=True)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""

    class Meta:
        list_serializer_class = FilterReviewSerializer

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class FolderSerializer(serializers.ModelSerializer):
    """Вывод папок"""

    class Meta:
        model = Folder
        fields = ("id", "name")

class DocumentSerializer(serializers.ModelSerializer):
    """Вывод документа"""
    children = RecursiveSerializer(many=True)
    perm = serializers.SerializerMethodField()
    document_logo = serializers.SerializerMethodField()
    folder = FolderSerializer()

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Document
        fields = (
            "id",
            "name",
            "children",
            "doc_uuid",
            "document_logo",
            "perm",
            "order_id",
            "data_row_order",
            "folder",
            'host_project',
            'content',
            'doc_order',
        )

    def get_perm(self, obj):
        user = self.context['request'].user
        perms = user.get_object_perm_as_str_list(obj)
        return perms[0] if len(perms) == 1 else perms

    def get_document_logo(self, obj):
        if obj.document_logo:
            return f"https://{self.context.get('request').META['HTTP_HOST']}" \
                   f"{MEDIA_URL}" \
                   f"{obj.document_logo}"
        else:
            return None


class ProjectSerializer(serializers.ModelSerializer):
    """Вывод проекта"""
    documents = DocumentSerializer(many=True)

    class Meta:
        model = Project
        fields = ("id", "documents")


def is_right_n(value):
    if not value in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
        raise serializers.ValidationError('недопустимое число')

def is_right_size(value):
    if not value in {0, 1, 2}:
        raise serializers.ValidationError('недопустимое число')

class ImageGenerationSerializer(serializers.Serializer):
    """ Вывод urls сгенерированных по описанию prompt изображений """
    prompt = serializers.CharField()
    n = serializers.IntegerField(required=False, default=1, validators=[is_right_n])
    size = serializers.IntegerField(required=False, default=2, validators=[is_right_size])
