import datetime

from rest_framework import serializers

from accounts.models import User
from bordomatic.serializers import BordomaticPrivateModelReadSerializer  #, BordomaticModelReadSerializer
from common.models import UserColumn
from common.serializers import (
    PpmDocSerializer,
    UserCellSerializer, UserColumnSerializer
)
from projects.models import Project
from storyboards.models import (
    Storyboard, Chrono, Frame, Shot, ChronoFrame)


class ShotSerializer(PpmDocSerializer):
    host_frame = serializers.PrimaryKeyRelatedField(
        queryset=Frame.objects.all(), write_only=True)

    class Meta:
        model = Shot
        fields = ['id', 'file', 'host_frame']


class FrameSerializer(PpmDocSerializer):
    shots = ShotSerializer(many=True, read_only=True)
    userfields = UserCellSerializer(many=True, read_only=True)
    host_storyboard = serializers.PrimaryKeyRelatedField(
        queryset=Storyboard.objects.all(), write_only=True)
    name = serializers.CharField(default=' ')

    class Meta:
        model = Frame
        fields = [
            'id',
            'name',
            'duration',
            'shots',
            'userfields',
            'host_storyboard'
        ]


class ChronoframeSerializer(PpmDocSerializer):
    host_chrono = serializers.PrimaryKeyRelatedField(
        queryset=Chrono.objects.all(),
        write_only=True
    )
    sbdframe = FrameSerializer(read_only=True)
    sbdframe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChronoFrame
        fields = [
            'id',
            'sbdframe',
            'sbdframe_id',
            'host_chrono'
        ]


class ChronoListSerializer(PpmDocSerializer):
    class Meta:
        model = Chrono
        fields = ['id', 'chronoframes']


class ChronoSerializer(PpmDocSerializer):
    frames = ChronoframeSerializer(
        source='chronoframes', many=True, read_only=True)
    host_storyboard = serializers.PrimaryKeyRelatedField(
        queryset=Storyboard.objects.all(), write_only=True)
    frame_order = serializers.ListField(
        child=serializers.IntegerField(),
        source='data_row_order',
        required=False
    )

    class Meta:
        model = Chrono
        fields = [
            'id', 'name', 'frames',
            'frame_order', 'col_order',
            'host_storyboard'
        ]


class FrameColumnSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField(read_only=True)
    column_id = serializers.IntegerField(source='id')
    frame_order = serializers.ListField(
        child=serializers.IntegerField(),
        source='data_row_order',
        required=False
    )

    class Meta:
        model = UserColumn
        fields = ['column_id', 'column_name', 'column_type', 'choices']

    def get_choices(self, instance):
        choices = [f"{ch.id}: {ch.choice}" for ch in instance.choices.all()]
        return choices


class StoryboardDetailSerializer(PpmDocSerializer):
    frame_columns = UserColumnSerializer(many=True, read_only=True)
    frames = FrameSerializer(many=True, read_only=True)
    chronos = ChronoSerializer(many=True, read_only=True)
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    last_modified_name = serializers.SerializerMethodField()
    last_modified_date = serializers.SerializerMethodField()
    frame_order = serializers.ListField(
        child=serializers.IntegerField(),
        source='data_row_order',
        required=False
    )
    perm = serializers.SerializerMethodField()

    bordomatic_private = BordomaticPrivateModelReadSerializer(many=True, required=False)
    #bordomatic = BordomaticModelReadSerializer(many=True, required=False)

    class Meta:
        model = Storyboard
        fields = [
            'id', 'name', 'description', 'tag_color',
            'frame_columns', 'frames', 'chronos',
            'frame_order', 'col_order',
            'host_project', 'perms', 'invites', 'doc_uuid',
            'last_modified_user', 'last_modified_date',
            'last_modified_name', 'perm',
            'frame_order', 'document_logo', 'bordomatic_private',
            'folder'  #'bordomatic'
        ]

    def get_last_modified_name(self, obj):
        user = User.objects.filter(email=obj.last_modified_user).first()
        if user:
            name = " ".join([user.first_name, user.last_name])
            return name.strip()

    def get_last_modified_date(self, obj):
        return int(datetime.datetime.timestamp(obj.last_modified_date))

    def get_perm(self, obj):
        user = self.context['request'].user
        project = obj.host_project
        perms = user.get_object_perm_as_str_list(project)
        return perms[0] if len(perms) == 1 else perms


# for debug
class StoryboardListSerializer(PpmDocSerializer):
    owner = serializers.StringRelatedField(source='owner.email')

    class Meta:
        model = Storyboard
        fields = ['id', 'name', 'owner', 'doc_uuid']
