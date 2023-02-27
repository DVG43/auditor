import time
from datetime import datetime

from common.serializers import PpmDocSerializer
from contacts.serializers import ContactSerializer
from projects.models import Project, Link, File, Text
from rest_framework import serializers
from poll.models.poll import Poll
from storyboards.models import Storyboard
from document.models import Document
from document.serializers import RecursiveSerializer
from timing.models import Timing
from folders.models import Folder
from accounts.models import User


class LastModifiedMixin(metaclass=serializers.SerializerMetaclass):
    """
    The mixin that adds three fields to sterilizers:
        * last_modified_name(str): first and last name
          of the user who made the last changes to the document;
        * last_modified_date(str): date of last change;
        * last_modified_time(str): time of last change;
    """
    last_modified_date = serializers.SerializerMethodField()
    # last_modified_time = serializers.SerializerMethodField()
    last_modified_name = serializers.SerializerMethodField()

    class Meta:
        fields = [
            'last_modified_name', 'last_modified_date'
        ]

    # def get_last_modified_time(self, instance) -> str:
    #     """Returns the time of the last document change in string format."""
    #     return datetime.strftime(instance.last_modified_date, '%H-%M')

    def get_last_modified_date(self, instance) -> str:
        """Returns the date of the last document change in string format."""
        return time.mktime(instance.last_modified_date.timetuple())

    def get_last_modified_name(self, instance) -> str:
        """Returns the first and last name of the user who made
        the last changes to the document in string format."""
        try:
            user = User.objects.get(email=instance.last_modified_user)
            return f'{user.first_name} {user.last_name}'
        # логирование
        except User.DoesNotExist:
            return ''


class FilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(deleted_id__isnull=True)
        if data.model == Document:
            data = data.filter(parent=None)
        return super(FilteredListSerializer, self).to_representation(data)


class RevStoryboardSerializer(serializers.ModelSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()

    class Meta:
        model = Storyboard
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'tag_color', 'doc_uuid',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'storyboard'


class RevPollSerializer(serializers.ModelSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'tag_color',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'poll'


class RevFolderSerializer(serializers.ModelSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'tag_color',
                  'last_modified_name',
                  'last_modified_date',
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'folder'


class RevDocumentSerializer(serializers.ModelSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()
    children = RecursiveSerializer(many=True)

    class Meta:
        model = Document
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'tag_color', 'doc_uuid',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder', 'children'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'document'


class RevTimingSerializer(serializers.ModelSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()

    class Meta:
        model = Timing
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'tag_color', 'doc_uuid',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'timing'


class LinkSerializer(PpmDocSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    perm = None
    invites = None

    class Meta:
        model = Link
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'url', 'tag_color', 'host_project',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'link'


class FileSerializer(PpmDocSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    perm = None
    invites = None

    class Meta:
        model = File
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'name', 'slugged_name',
                  'file', 'tag_color', 'host_project',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'file'


class TextSerializer(PpmDocSerializer, LastModifiedMixin):
    model = serializers.SerializerMethodField()
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    perm = None
    invites = None

    class Meta:
        model = Text
        list_serializer_class = FilteredListSerializer
        fields = ['id', 'model', 'text', 'tag_color', 'host_project',
                  'order_id', 'document_logo',
                  'last_modified_name',
                  'last_modified_date',
                  'folder'
                  # 'last_modified_time',
                  ]

    def get_model(self, obj):
        return 'text'


class RevDocSerializer(serializers.Serializer):
    documents = RevDocumentSerializer(
        many=True, read_only=True)
    timings = RevTimingSerializer(
        many=True, read_only=True)
    polls = RevPollSerializer(
        many=True, read_only=True)
    links = LinkSerializer(
        many=True, read_only=True)
    files = FileSerializer(
        many=True, read_only=True)
    texts = TextSerializer(
        many=True, read_only=True)
    folders = RevFolderSerializer(
        many=True, read_only=True)


class ProjectDetailSerializer(PpmDocSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'logo',
            'invites',
            'contacts',
            'doc_order',
        ]


class ProjectListSerializer(PpmDocSerializer, LastModifiedMixin):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'logo',
            'invites',
            'documents',
            'doc_order',
            'last_modified_name',
            'last_modified_date',
            # 'last_modified_time'
        ]

    def get_documents(self, instance):
        return RevDocSerializer(instance, context=self.context).data


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['contacts']
