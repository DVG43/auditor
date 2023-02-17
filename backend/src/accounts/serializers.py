from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import settings
from accounts.utils import generate_code, send_activation_email, crm_contact_check

User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    error_messages = {
        "blank": "field can not be blank",
        "required": "field required",
        "invalid": "invalid"
    }
    first_name = serializers.CharField(
        allow_blank=False,
        min_length=2,
        error_messages={
            "min_length": "length must be 2 or more symbols",
            **error_messages
        }
    )
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        allow_blank=False,
        error_messages={
            "min_length": "length must be 6 or more symbols",
            **error_messages
        }
    )
    email = serializers.CharField(
        allow_blank=False,
        error_messages=error_messages
    )
    new_email = serializers.CharField(
        allow_blank=False,
        error_messages=error_messages
    )
    code = serializers.CharField(
        allow_blank=False,
        min_length=4,
        max_length=4,
        error_messages={
            "min_length": "length must be 4 symbols",
            "max_length": "length must be 4 symbols",
            **error_messages
        }
    )
    old_password = serializers.CharField(
        min_length=6,
        error_messages={
            "min_length": "minimum length 6 symbols",
            **error_messages
        }
    )
    new_password = serializers.CharField(
        min_length=6,
        error_messages={
            "min_length": "minimum length 6 symbols",
            **error_messages
        }
    )
    refresh = serializers.CharField(
        min_length=128,
        required=True,
        error_messages=error_messages
    )

    class Meta:
        abstract = True


class UserSerializer(AccountSerializer):
    subscription_trial = serializers.BooleanField(
        source='subscription.tariff.is_trial', read_only=True, allow_null=True)
    subscription_end = serializers.IntegerField(
        source='subscription.end_date', read_only=True, allow_null=True)
    oauth2_providers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name', 'last_name',
            'phone',
            'birthday',
            'password',
            'avatar',
            'subscription_trial',
            'subscription_end',
            'is_invited',
            'is_verified',
            'document',
            'disk_space',
            'contacts_order',
            'changed_password_date',
            'user_language',
            'oauth2_providers'
        ]
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        try:
            user = User.objects.get(email=validated_data['email'].lower())
        except ObjectDoesNotExist:
            user = super().create(validated_data)
        if user.is_verified:
            raise ValidationError({'error': 'address already exists'})
        else:
            # если юзер не подтвержден (т.е. явлется приглашенным, то обновляем его данные из формы)
            user.is_verified = False
            user = super().update(user, validated_data)
        user.set_password(validated_data['password'])
        user.code = generate_code()
        user.save()
        send_activation_email(user)
        if not settings.DEBUG:
            print("Sending crm_contact_check, user =", user)
            crm_contact_check(user)
            print("Sent")
        return user

    def create_social(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.is_verified = True
        user.save()
        if not settings.DEBUG:
            print("Sending crm_contact_check, user =", user)
            crm_contact_check(user)
            print("Sent")
        return user

    def get_oauth2_providers(self, obj):
        providers = [soc_user.provider for soc_user in obj.social_auth.all()]
        return providers


class EmailVerifySerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['code', 'email', 'password']


class LoginSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']


class ChangePasswordSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['old_password', 'new_password']


class ResetPasswordSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['email']


class ChangeEmailSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['new_email']


class ChangeEmailConfirmSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['new_email', 'code']


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)


class RefreshTokenSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['refresh']


class LogoutViewSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['refresh']


class DocUUIDViewSerializer(serializers.Serializer):
    doc_uuid = serializers.UUIDField()


class DocAccessSerializer(serializers.Serializer):
    doc_id = serializers.IntegerField()
    model = serializers.CharField()


class SocialAuthSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(
        max_length=4096,
        required=True,
        trim_whitespace=True
    )


class SocialAuthDisconnectSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)


class AddEmailAfterOauthSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['new_email', 'new_password']


class AddEmailConfirmSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = ['code']
