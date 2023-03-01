from rest_framework import serializers

from common.serializers import PpmDocSerializer
from folders.models import Folder
from projects.serializers import RevDocSerializer, FilteredListSerializer


class FolderDocsSerializer(RevDocSerializer):
    pass


class FolderSerializer(PpmDocSerializer):
    child_folders = serializers.SerializerMethodField()
    folder_objects = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        list_serializer_class = FilteredListSerializer
        fields = [
            'id', 'name',
            'folder_objects',
            'parent_folder',
            'doc_order',
            'order_id',
            'child_folders',
            'document_logo'
        ]
        read_only_fields = [
            'last_modified_user',
            'last_modified_date',
        ]

    def get_child_folders(self, obj):
        data = self._get_folders_tree(obj)
        return data

    def get_folder_objects(self, instance):
        return FolderDocsSerializer(instance, context=self.context).data

    def _get_folders_tree(self, obj):
        child_folders = list()
        folders = obj.folders.filter(deleted_id__isnull=True)
        if folders:
            for folder in folders:
                child_folders.append(
                    FolderSerializer(folder, context=self.context).data
                )
            return child_folders
        return None


class FolderListSerializer(PpmDocSerializer):

    class Meta:
        model = Folder
        list_serializer_class = FilteredListSerializer
        fields = [
            'id',
            'parent_folder',
            'name',
            'last_modified_user',
            'last_modified_date',
            'document_logo'
        ]
