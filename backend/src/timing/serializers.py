from accounts.models import User
from common.serializers import PpmDocSerializer
from rest_framework import serializers

from projects.models import Project
from timing.models import Timing, Event, TimingGroup


class TimingSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()
    host_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), write_only=True)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)
    document_logo_url = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = Timing
        fields = '__all__'

    def get_model(self, obj):
        return 'timing'


class TimingUpdateSerializer(TimingSerializer):
    name = serializers.CharField(max_length=255, required=False)


class EventSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()
    host_group = serializers.PrimaryKeyRelatedField(
        queryset=TimingGroup.objects.all(), write_only=True)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = Event
        fields = '__all__'

    def get_model(self, obj):
        return 'event'


class GroupSerializer(PpmDocSerializer):
    model = serializers.SerializerMethodField()
    host_timing = serializers.PrimaryKeyRelatedField(
        queryset=Timing.objects.all(), write_only=True)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = TimingGroup
        fields = '__all__'

    def get_model(self, obj):
        return 'group'
