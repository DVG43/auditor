import datetime
import time
import uuid
from smtplib import SMTPRecipientsRefused
from urllib.error import HTTPError

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, \
    TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts import serializers
from accounts.tasks import crm_deal_update
from accounts.utils import (
    generate_code,
    send_activation_email,
    send_reset_password_email,
    send_change_email)
from accounts.permissions import IsActivated
from common.utils import get_model, check_file_size, recount_disk_space, like_or_dislike_object
from contacts.models import Department, Position
from objectpermissions.models import UserPermission
from document.models import Document
from social_core.utils import user_is_active
from social_django.utils import psa, load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from storyboards.models import Storyboard
from subscription.models import Subscription, Tariff
from subscription.utils import check_or_create_subscription_objects

import requests

from table.models import DefaultTableModel
from timing.models import Timing

User = get_user_model()


def get_profile_with_tokens(user, email, password):
    login_data = {'email': email, 'password': password}
    serialized_token_data = TokenObtainPairSerializer(data=login_data)
    serialized_token_data.is_valid(raise_exception=True)
    token_data = serialized_token_data.validated_data
    user_data = serializers.UserSerializer(instance=user).data
    response_data = user_data
    response_data.update(token_data)
    return response_data


def check_obj_class(doc_uuid):
    storyboard_obj = Storyboard.objects.filter(
        doc_uuid=doc_uuid).first()
    document_obj = Document.objects.filter(
        doc_uuid=doc_uuid).first()
    timing_obj = Timing.objects.filter(
        doc_uuid=doc_uuid).first()
    table_obj = DefaultTableModel.objects.filter(
        doc_uuid=doc_uuid).first()
    if storyboard_obj:
        return storyboard_obj
    elif document_obj:
        return document_obj
    elif timing_obj:
        return timing_obj
    elif table_obj:
        return table_obj
    else:
        return None


def create_default_positions_and_departments(user):
    BASE_DEPARTMENTS = [
        'Клиенты', 'Агентства', 'Административная группа', 'Режиссёрская группа',
        'Операторская группа', 'Осветительная группа', 'Художественно-постановочная группа',
        'Актёры'
    ]
    BASE_POSITIONS = [
        'Клиент', 'Агентство', 'Генеральный продюсер', 'Исполнительный продюсер', 'Продюсер',
        'Директор группы', 'Заместитель директора', 'Администратор', 'Рабочие', 'Буфет',
        'Режиссёр', 'Второй режиссёр', 'Режисcёр монтажа', 'Оператор постановщик', 'Стэдикам',
        'Механик камеры', 'Фокус пуллер', 'Долли', 'Кран', 'Гафер', 'Осветители', 'Кей грипп',
        'Пультовик', 'Художник постановщик', 'Ассистент художника', 'Реквизитор', 'Бутафор',
        'Художник по костюмам', 'Художник по гриму', 'Актёр'
    ]
    for dep in BASE_DEPARTMENTS:
        Department.objects.create(owner=user, name=dep, tag_color='purple')
    for pos in BASE_POSITIONS:
        Position.objects.create(owner=user, name=pos, tag_color='purple')


def verify_user(user):
    if not user.is_verified:
        user.is_verified = True
        user.is_active = True
        user.code = None
        user.last_login = timezone.now()
        trial_tariff = get_object_or_404(Tariff, is_trial=True)
        trial_period = float(trial_tariff.periods.first().month_amount)
        trial_end_date = timezone.now() + datetime.timedelta(days=trial_period * 30)
        trial_end_unix = int(time.mktime(trial_end_date.timetuple()))
        Subscription.objects.create(
            user=user,
            tariff=trial_tariff,
            tariffs_id=1,
            end_date=trial_end_unix
        )
        crm_deal_update.delay(user.b24_deal_id, 'email_verified')
        create_default_positions_and_departments(user)
        user.save()
        instances = UserPermission.objects.filter(user_id=user.pkid).all()
        for instance in instances:
            instance.save()


class UserViewSet(viewsets.ModelViewSet):
    throttle_scopes = 'users'
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        request.data.update({'email': email.lower()})
        check_or_create_subscription_objects()
        try:
            super().create(request)
        except SMTPRecipientsRefused:
            print('Wrong email')
        return Response({'success': 'verification code was sent'},
                        status=status.HTTP_201_CREATED)

    def get_permission_classes(self):
        if self.action == 'post':
            return [AllowAny]
        else:
            return [IsAuthenticated, IsActivated]

    def get_object(self):
        if self.request.user.pk:
            user = User.objects.filter(pk=self.request.user.pk)
            if user:
                return user.first()
        else:
            raise ValidationError({'error': 'token not provided'})

    def partial_update(self, request, *args, **kwargs):
        # проверяем, что для загружаемого файла достаточно места на диске
        if not check_file_size(request, request.user) and request.FILES:
            return Response({'file': 'Not enough space on disk for file'},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'email' in request.data:
            request.data.pop('email')
        if 'password' in request.data:
            request.data.pop('password')
        response = super().partial_update(request, *args, **kwargs)

        if response and request.FILES:
            # пересчитываем место на диске после добавление обновленного файла
            user = User.objects.filter(pkid=request.user.pkid).first()
            disk_space = recount_disk_space(request.user)
            user.disk_space = disk_space
            user.save()
            response.data.update({"disk_space": disk_space})
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        Subscription.objects.filter(user_id=instance.pkid).delete()
        instance.is_active = False
        instance.is_verified = False
        instance.code = None
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsActivated]

    def partial_update(self, request):
        like = like_or_dislike_object(request.user, 'bordomatic')
        return Response({'like': like})

    def retrieve(self, request):
        return Response({'total': User.objects.filter(like=True).count()})

    def update_doc_like(self, request):
        like = like_or_dislike_object(request.user, 'document')
        return Response({'like': like})

    def get_total_likes(self, request):
        return Response({'total': User.objects.filter(document_like=True).count()})

    def get_doc_like(self, request):
        user = User.objects.filter(pkid=request.user.pkid).first()
        return Response({'like': user.document_like})


class ResendActivationCode(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ResendCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user = User.objects.filter(email=data['email'])
        if user:
            user = user.first()
            if not user.is_verified:
                user.code = generate_code()
                user.save()
                send_activation_email(user)
                return Response({'success': 'code was sent'})
            else:
                return Response({'success': 'email already verified'})
        else:
            raise ValidationError({'email': 'not found'})


class EmailVerifyView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.EmailVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        code = serializer.validated_data['code']

        user = User.objects.filter(email=email)
        if not user:
            raise ValidationError({'email': 'wrong email'})
        user = user.first()
        if not user.check_password(password):
            raise ValidationError({'password': 'wrong password'})

        if code == user.code:
            if not user.is_verified:
                verify_user(user)
                response_data = get_profile_with_tokens(user, email, password)
                return Response(response_data)
        elif user.is_verified:
            field = 'email'
            err = 'account already activated'
        else:
            field = 'code'
            err = 'wrong code'
        raise ValidationError({field: err})


class LoginView(generics.CreateAPIView):
    serializer_class = serializers.LoginSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data['email'].lower()
        password = data['password']
        user = User.objects.filter(email=email)
        if not user or not user.first().check_password(password):
            return Response(
                {'auth': 'wrong credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif user.first().is_active and not user.first().is_verified:
            return Response(
                {'auth': 'email not verified'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif not user.first().is_active:
            return Response(
                {'auth': 'wrong credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = user.first()
        user.last_login = timezone.now()
        user.save()
        response_data = get_profile_with_tokens(user, email, password)
        return Response(response_data)


class ChangePasswordAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsActivated]
    serializer_class = serializers.ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        data = serializer.validated_data
        old_password = data['old_password']
        new_password = data['new_password']

        if not user.check_password(old_password):
            raise ValidationError({'old_password': ['wrong']})

        if old_password == new_password:
            raise ValidationError(
                {'new_password': ['can not match old_password']})

        user.set_password(new_password)
        user.changed_password_date = timezone.now()
        user.save()

        return Response({'success': 'password changed'})


class ResetPasswordAPIView(generics.CreateAPIView):
    throttle_scope = 'password_reset'
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        user = User.objects.filter(email=email)
        if not user:
            raise ValidationError({'email': 'not found'})
        else:
            user = user.first()
        password = User.objects.make_random_password()
        user.set_password(password)
        user.changed_password_date = timezone.now()
        user.save()
        send_reset_password_email(user, password)
        return Response({'success': 'new password was sent'})


class ChangeEmail(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsActivated]
    serializer_class = serializers.ChangeEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user
        user.code = generate_code()
        user.save()

        new_email = data['new_email'].lower()
        send_change_email(user, new_email)

        return Response({'success': 'code was sent'})


class ChangeEmailConfirm(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsActivated]
    serializer_class = serializers.ChangeEmailConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = self.request.user
        new_email = data['new_email'].lower()
        code = data['code']

        if not user.code:
            raise ValidationError({'code': 'send change email request first'})

        if code == user.code:
            user.email = new_email
            user.code = None
            user.save()
            return Response({'success': 'email changed'})
        else:
            raise ValidationError({'code': 'wrong'})


class RefreshTokenView(generics.CreateAPIView):
    serializer_class = serializers.RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refresh_serializer = TokenRefreshSerializer(data=data)
        try:
            refresh_serializer.is_valid(raise_exception=True)
        except TokenError:
            raise ValidationError({'refresh': 'wrong refresh token'})
        return Response(refresh_serializer.validated_data)


class LogoutView(generics.CreateAPIView):
    """
    Заносит refresh токен в чёрный список
    """
    permission_classes = [IsAuthenticated, IsActivated]
    serializer_class = serializers.LogoutViewSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = RefreshToken(serializer.validated_data['refresh_token'])
        token.blacklist()

        return Response({'success': 'successful logout'})


class ShareDocView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsActivated]
    serializer_class = serializers.DocAccessSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=dict(request.data))
        serializer.is_valid(raise_exception=True)
        obj = get_model(serializer.validated_data["model"]).objects.filter(
            id=serializer.validated_data["doc_id"]).first()

        if not obj:
            raise ValidationError({'data': 'wrong document ID or document type'})

        doc_uuid = uuid.uuid4()
        obj.doc_uuid = doc_uuid
        obj.save()

        return Response({
            'doc_uuid': str(doc_uuid)
        })

    def delete(self, request, doc_uuid):
        instance = check_obj_class(doc_uuid)

        if not instance:
            raise ValidationError({'doc_uuid': 'wrong document UUID'})

        instance.doc_uuid = None
        instance.save()

        user = User.objects.filter(document=doc_uuid).first()
        if not user:
            return Response(status=status.HTTP_204_NO_CONTENT)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetSharedDoc(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = serializers.DocUUIDViewSerializer

    def retrieve(self, request, doc_uuid):

        user = User.objects.filter(document=doc_uuid).first()
        instance = check_obj_class(doc_uuid)
        if not instance:
            raise ValidationError({'doc_uuid': 'wrong document UUID'})

        if not user:
            user = User(email='1' + '@' + str(doc_uuid) + '.com',
                        is_invited=True, document=doc_uuid)
            user.set_password(str(doc_uuid))
            user.save()
            user.grant_object_perm(instance, 'read')
            user.save()

        response_data = get_profile_with_tokens(user, user.email, str(doc_uuid))
        return Response(response_data)


class SocialComplete(APIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SocialAuthSerializer

    def post(self, request):
        """Authenticate user through the provider and access_token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.data.get('provider', None)
        strategy = load_strategy(request)

        try:
            backend = load_backend(strategy=strategy, name=provider,
                                   redirect_uri=None)

        except MissingBackend:
            return Response({'error': 'Please provide a valid provider'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            if isinstance(backend, BaseOAuth2):
                access_token = serializer.data.get('access_token')
            if isinstance(request.user, AnonymousUser):
                user = backend.do_auth(access_token)
                sub = Subscription.objects.filter(user=user)
                if not sub:
                    verify_user(user)
                    user.is_verified = False
                    user.save()
            else:
                user = request.user
        except HTTPError as error:
            return Response({
                "error": {
                    "access_token": "Invalid token",
                    "details": str(error)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except AuthTokenError as error:
            return Response({
                "error": "Invalid credentials",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            authenticated_user = backend.do_auth(access_token, user=user)

        except HTTPError as error:
            return Response({
                "error": "invalid token",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        except AuthForbidden as error:
            return Response({
                "error": "invalid token",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

        if authenticated_user and authenticated_user.is_active:
            data = serializers.UserSerializer(instance=user).data

            refresh = RefreshToken.for_user(user)
            tokens_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            data.update(tokens_data)
            return Response(status=status.HTTP_200_OK, data=data)


class SocialDisconnect(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.SocialAuthDisconnectSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate user through the provider and access_token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.data.get('provider', None)
        user = request.user
        social_auth_account = user.social_auth.filter(provider=provider).first()
        if social_auth_account:
            print(social_auth_account.provider)
            social_auth_account.delete()
            return Response({'oauth2_providers': f'{provider} is disconnected'})
        raise ValidationError(
            {'oauth2_providers': [f'user have not oauth provider {provider}']}
        )


class AddEmailAfterOauthAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddEmailAfterOauthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        data = serializer.validated_data

        new_email = data['new_email']
        new_password = data['new_password']

        oauth2_providers = user.social_auth.all()

        if new_email != request.user.email:
            email_user = User.objects.filter(email=new_email)
            if email_user:
                raise ValidationError(
                        {'new_password': ['email already taken']})
            else:
                user.email = new_email

        if not oauth2_providers:
            raise ValidationError(
                    {'oauth2_providers': ['user have not oauth providers']})
        user.set_password(new_password)
        user.changed_password_date = timezone.now()
        user.code = generate_code()
        user.save()

        send_change_email(user, new_email)

        return Response({'success': 'code was sent'})


class AddEmailAfterOauthConfirm(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddEmailConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = self.request.user
        code = data['code']

        if not user.code:
            raise ValidationError({'code': 'send change email request first'})

        if code == user.code:
            user.is_verified = True
            user.code = None
            user.save()
            return Response({'success': 'email changed'})
        else:
            raise ValidationError({'code': 'wrong'})
