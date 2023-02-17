from rest_framework import serializers

from common.serializers import PpmDocSerializer
from folders.models import Folder
from projects.serializers import RevDocSerializer


class FolderDocsSerializer(RevDocSerializer):
    pass


class FolderSerializer(PpmDocSerializer):
    child_folders = serializers.SerializerMethodField()
    folder_objects = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = [
            'id', 'tag_color', 'name',
            'host_project',
            'last_modified_user', 'last_modified_date',
            'parent_folder', 'child_folders',
            'folder_objects'
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
    class Meta:
        model = Folder
        fields = [
            'id',
            'parent_folder',
            'tag_color',
            'name'
        ]
