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
            'last_modified_user', 'last_modified_date',
            'parent_folder', 'child_folders',
            'folder_objects', 'deleted_id'
        ]

    def get_child_folders(self, obj):
        data = self._get_folders_tree(obj)
        return data

    def get_folder_objects(self, instance):
        return FolderDocsSerializer(instance, context=self.context).data

    def _get_folders_tree(self, obj):
        tree = dict()
        folders = obj.folders.all()
        if folders:
            for folder in folders:
                tree.update({folder.id: self._get_folders_tree(folder)})
            return tree
        return None


class FolderListSerializer(PpmDocSerializer):
    child_head_folders = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        list_serializer_class = FilteredListSerializer
        fields = [
            'id',
            'parent_folder',
            'tag_color',
            'name',
            'child_head_folders'
        ]

        def get_child_head_folders(self, obj):
            return FolderSerializer(obj, context=self.context, many=True, read_only=True).data
