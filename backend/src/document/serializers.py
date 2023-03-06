from common.serializers import PpmDocSerializer
from document.models import Document
from rest_framework import serializers
from settings import MEDIA_URL
from projects.models import Project


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


class DocumentSerializer(serializers.ModelSerializer):
    """Вывод документа"""
    children = RecursiveSerializer(many=True)
    perm = serializers.SerializerMethodField()
    document_logo = serializers.SerializerMethodField()
    folder_id = serializers.IntegerField(source='folder.id')
    folder_name = serializers.CharField(source='folder.name')

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
            "folder_id",
            "folder_name",
            'host_project',
            'content',
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

class TextRephraseSerializer(serializers.Serializer):
    """Ввод текста для перефразирования"""
    source = serializers.CharField()
    max_tokens = serializers.IntegerField(required=False)

class TextGenerationSerializer(TextRephraseSerializer):
    """Ввод текста для генерации"""
    tone = serializers.ChoiceField(choices={
            "grateful",
            "excited",
            "rude",
            "sad",
            "informative",
            "witty",
            "negative",
            "neutral",
            "positive",
            "professional",
            "convincing",
            "engaging",
            "humorous"
        },
        required=False,
        allow_null=True)
    language = serializers.CharField(required=False)
    keywords = serializers.CharField(required=False)
