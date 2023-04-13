from rest_framework import serializers
from portal.models import Portal


class PortalSerializer(serializers.Serializer):

    class Meta:
        model = Portal
        fields = '__all__'
