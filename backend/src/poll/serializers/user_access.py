from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import serializers

from poll.query import get_or_none
from poll.models.user_access import UserAccess, Invitations
from poll.utils import USER_ROLE, USER_ACCESS_TIME_FORMAT

User = get_user_model()


class UserAccessSerializer(serializers.ModelSerializer):

    poll = serializers.ReadOnlyField(source='poll.pk')
    user = serializers.ReadOnlyField(source='user.email')
    first_name = serializers.ReadOnlyField(source='user.secretguestprofile.first_name')
    last_name = serializers.ReadOnlyField(source='user.secretguestprofile.last_name')
    user_id = serializers.ReadOnlyField(source='user.id')
    updated_at = serializers.DateTimeField(read_only=True, format=USER_ACCESS_TIME_FORMAT)
    created_at = serializers.DateTimeField(read_only=True, format=USER_ACCESS_TIME_FORMAT)

    class Meta:
        model = UserAccess
        fields = ['role', 'user', 'user_id', 'poll', 'updated_at', 'created_at', 'first_name', 'last_name']

    def to_representation(self, instance):
        resp = super(UserAccessSerializer, self).to_representation(instance)
        resp['type'] = 'access'
        return resp


class UserAccessRequestSerializer(serializers.Serializer):
    emailArray = serializers.ListSerializer(
        child=serializers.EmailField(allow_blank=True)
    )
    role = serializers.ChoiceField(choices=USER_ROLE, allow_blank=False, required=True)
    messageText = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        poll = self.context['poll']
        emails = validated_data.get('emailArray', [])
        message_text = validated_data.get('messageText', '')
        for email in emails:
            user = get_or_none(User, email=email)

            if user is not None:
                UserAccess.objects.update_or_create(
                    user=user,
                    poll=poll,
                    defaults={
                        'role': validated_data['role']
                    }
                )
            else:
                Invitations.objects.update_or_create(
                    email=email,
                    poll=poll,
                    defaults={
                        'role': validated_data['role']
                    }
                )
        if emails and len(message_text) > 0:
            subject = f'Вы получили доступ к форме "{poll.title}"'
            send_mail(subject, message_text, settings.EMAIL_HOST_USER, emails)
        return validated_data


class InvitationSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(read_only=True, format=USER_ACCESS_TIME_FORMAT)
    created_at = serializers.DateTimeField(read_only=True, format=USER_ACCESS_TIME_FORMAT)

    class Meta:
        model = Invitations
        fields = ['email', 'role', 'updated_at', 'created_at']

    def to_representation(self, instance):
        resp = super(InvitationSerializer, self).to_representation(instance)
        resp['type'] = 'invitation'
        return resp
