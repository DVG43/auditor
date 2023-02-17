import datetime
from pprint import pprint

from rest_framework import serializers

from accounts.models import User
from common.serializers import (
    PpmDocSerializer,
    UserCellSerializer,
    UserColumnSerializer
)
from projects.models import Project
from shootingplans.models import Shootingplan, Unit, Unitframe
from storyboards.serializers import FrameSerializer


class UnitframeSerializer(PpmDocSerializer):
    userfields = UserCellSerializer(many=True, read_only=True)
    sbdframe = FrameSerializer(read_only=True)
    sbdframe_id = serializers.IntegerField(write_only=True, required=False)
    host_unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        write_only=True
    )

    class Meta:
        model = Unitframe
        fields = [
            'id', 'duration', 'description',
            'sbdframe', 'sbdframe_id',
            'userfields',
            'host_unit'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not ret['sbdframe']:
            ret.pop('sbdframe')
        return ret


class UnitListSerializer(PpmDocSerializer):
    class Meta:
        model = Unit
        fields = [
            'id', 'name'
        ]


class UnitSerializer(PpmDocSerializer):
    sbdframe_columns = serializers.SerializerMethodField()
    frame_columns = UserColumnSerializer(many=True, read_only=True)
    frames = UnitframeSerializer(
        source='unitframes', many=True, read_only=True)
    host_shootingplan = serializers.PrimaryKeyRelatedField(
        queryset=Shootingplan.objects.all(), write_only=True)
    frame_order = serializers.ListField(
        child=serializers.IntegerField(),
        source='data_row_order',
        required=False
    )

    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'description', 'day_start',
            'sbdframe_columns', 'frame_columns', 'frames',
            'host_shootingplan',
            'frame_order', 'col_order'
        ]

    def get_sbdframe_columns(self, obj):
        sbdframe_columns = []
        for unitframe in obj.unitframes.all():
            x = unitframe.sbdframe
            if x:
                sbdframe_columns = x.host_storyboard.frame_columns.all()
                break
        serializer = UserColumnSerializer(instance=sbdframe_columns, many=True)
        return serializer.data


class ShootingplanSerializer(PpmDocSerializer):
    units = UnitSerializer(many=True, read_only=True)
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    host_storyboard = serializers.PrimaryKeyRelatedField(
        source='host_project.storyboards.first', read_only=True
    )
    last_modified_name = serializers.SerializerMethodField()
    last_modified_date = serializers.SerializerMethodField()

    perm = serializers.SerializerMethodField()

    class Meta:
        model = Shootingplan
        fields = [
            'id', 'name', 'date', 'description', 'tag_color',
            'units', 'host_storyboard',
            'host_project', 'doc_uuid',
            'last_modified_user', 'last_modified_date',
            'last_modified_name', 'perm', 'document_logo',
            'folder'
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


class ShootingplanListSerializer(PpmDocSerializer):
    class Meta:
        model = Shootingplan
        fields = ['id', 'name', 'date', 'owner', 'doc_uuid']


class ShootingplanCalendarSerializer(serializers.ModelSerializer):
    host_project_id = serializers.IntegerField(source='host_project.id')
    host_project_name = serializers.CharField(source='host_project.name')

    class Meta:
        model = Shootingplan
        fields = [
            'id', 'name', 'description', 'date',
            'host_project_id', 'host_project_name'
        ]
