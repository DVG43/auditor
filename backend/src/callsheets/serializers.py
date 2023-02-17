import datetime
from pprint import pprint

from rest_framework import serializers

from accounts.models import User
from callsheets.models import (
    Callsheet,
    Location,
    CallsheetLogo,
    LocationMap,
    Callsheetmember,
)
from common.serializers import PpmDocSerializer, UserCellSerializer, \
    UserColumnSerializer
from contacts.models import Department, Position
from projects.models import Project


class CallsheetLogoSerializer(PpmDocSerializer):
    file = serializers.ImageField()
    host_callsheet = serializers.PrimaryKeyRelatedField(
        queryset=Callsheet.objects.all(), write_only=True)

    class Meta:
        model = CallsheetLogo
        fields = ['id', 'file', 'host_callsheet']


class LocationMapSerializer(PpmDocSerializer):
    file = serializers.FileField()
    host_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), write_only=True)

    class Meta:
        model = LocationMap
        fields = ['id', 'file', 'host_location']


class LocationSerializer(PpmDocSerializer):
    userfields = UserCellSerializer(many=True, read_only=True)
    host_callsheet = serializers.PrimaryKeyRelatedField(
        queryset=Callsheet.objects.all(), write_only=True)
    maps = LocationMapSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = [
            'id',
            'address',
            'maps',
            'check_in',
            'check_out',
            'start_motor',
            'stop_motor',
            'shift_type',
            'userfields',
            'host_callsheet'
        ]


class CallsheetListSerializer(PpmDocSerializer):
    class Meta:
        model = Callsheet
        fields = ['id', 'name', 'date', 'doc_uuid']


class CallsheetmemberSerializer(PpmDocSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True)
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(), required=False, allow_null=True)
    department_title = serializers.CharField(
        source='department.name', read_only=True)
    department_color = serializers.CharField(
        source='department.tag_color', read_only=True)
    position_title = serializers.CharField(
        source='position.name', read_only=True)
    position_color = serializers.CharField(
        source='position.tag_color', read_only=True)
    host_callsheet = serializers.PrimaryKeyRelatedField(
        queryset=Callsheet.objects.all(), write_only=True
    )
    userfields = UserCellSerializer(many=True, required=False)

    class Meta:
        model = Callsheetmember
        fields = [
            'id', 'name', 'phone', 'email',
            'department', 'department_title', 'department_color',
            'position', 'position_title', 'position_color',
            'userfields',
            'host_callsheet',
        ]

    # def update(self, instance, validated_data):
    #     print(101,'CallsheetmemberSerializer', instance, validated_data)
    #     if 'position' in validated_data:
    #         pos_id = validated_data.pop('position')
    #         instance.position_id = pos_id['id']
    #     if 'department' in validated_data:
    #         dep_id = validated_data.pop('department')
    #         instance.department_id = dep_id['id']
    #     instance.save()
    #     return super().update(instance, validated_data)


class CallsheetSerializer(PpmDocSerializer):
    members = CallsheetmemberSerializer(many=True, required=False)
    member_columns = UserColumnSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    userfields = UserCellSerializer(many=True, read_only=True)
    logos = CallsheetLogoSerializer(
        source='callsheet_logos', many=True, read_only=True)
    project_name = serializers.StringRelatedField(
        source='host_project.name', read_only=True)
    project_id = serializers.IntegerField(
        source='host_project.id', read_only=True)
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    last_modified_name = serializers.SerializerMethodField()
    last_modified_date = serializers.SerializerMethodField()
    location_order = serializers.ListField(
        child=serializers.IntegerField(),
        source='data_row_order',
        required=False
    )
    perm = serializers.SerializerMethodField()

    class Meta:
        model = Callsheet
        fields = [
            'id', 'tag_color', 'name',
            'project_id', 'project_name',
            'date', 'description', 'logos', 'contact',
            'film_day', 'start_time', 'end_time',
            'lunch_type', 'lunch_time', 'shift_type',
            'sunrise', 'sunset', 'weather',
            'temp', 'max_temp', 'min_temp',
            'city', 'lat', 'lng',
            'userfields',
            'locations',
            'member_columns',
            'members',
            'host_project',
            'doc_uuid',
            'last_modified_user', 'last_modified_date',
            'last_modified_name', 'perm',
            'location_order', 'document_logo',
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


class CallsheetCalendarSerializer(serializers.ModelSerializer):
    host_project_id = serializers.IntegerField(source='host_project.id')
    host_project_name = serializers.CharField(source='host_project.name')

    class Meta:
        model = Callsheet
        fields = ['id', 'name', 'description', 'date',
                  'host_project_id', 'host_project_name']
