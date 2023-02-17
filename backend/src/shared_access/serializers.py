from rest_framework import serializers


class ShareProjectSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    perm = serializers.CharField(required=True)
    message = serializers.CharField()


class ShareFolderSerializer(ShareProjectSerializer):
    email = serializers.EmailField(required=True)
    perm = serializers.CharField(required=True)
    message = serializers.CharField()


class ShareDeleteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
