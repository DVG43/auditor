import os
import settings
from rest_framework import serializers
from common.serializers import PpmDocSerializer
from folders.models import Folder


class TrashDocSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    model = serializers.SerializerMethodField()
    name = serializers.CharField()
    folder = serializers.SerializerMethodField()
    deleted_id = serializers.UUIDField()
    deleted_since = serializers.DateTimeField()
    doc_size = serializers.SerializerMethodField()

    def get_model(self, obj):
        return obj.__class__.__name__.lower()

    def get_folder(self, obj):
        if self.get_model(obj) == 'folder':
            return obj.parent_folder.name
        else:
            return obj.folder.name

    def get_doc_size(self, obj):
        owner_id = obj.owner_id
        doc_name = obj.__class__.__name__.lower()
        doc_id = obj.id
        root_folder = os.path.join(os.getcwd(), settings.MEDIA_ROOT, str(owner_id))
        size = 0
        if doc_name == 'file':
            size += obj.file.size
        else:
            folder = f'{root_folder}/{doc_name}/{doc_id}/'
            for path, dirs, files in os.walk(folder):
                for f in files:
                    fp = os.path.join(path, f)
                    size += os.path.getsize(fp)
        return size


class TrashFolderListSerializer(PpmDocSerializer):
    documents = serializers.SerializerMethodField()
    folder = serializers.CharField(source='name')
    doc_size = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = [
            'id',
            'name',
            'deleted_id',
            'deleted_since',
            'doc_size',
            'documents',
            'folder'

        ]

    def get_documents(self, obj):
        docs = []
        rel_docs = settings.REL_DOCS
        for doc_type in rel_docs:
            for doc in getattr(obj, doc_type).filter(deleted_id__isnull=False):
                if doc:
                    docs.append(doc)
        serializer = TrashDocSerializer(docs, many=True)
        return serializer.data

    def get_doc_size(self, obj):
        size = 0
        data = self.get_documents(obj)
        for doc in data:
            size += doc['doc_size']
        return size
