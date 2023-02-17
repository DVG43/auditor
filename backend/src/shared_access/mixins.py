import datetime
import django
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from rest_framework.exceptions import ValidationError

from accounts.models import User
from objectpermissions.models import UserPermission
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from common.models import PERMS, permissions
from settings import ALLOWED_HOSTS


class ShareMixin(ModelViewSet):
    @action(detail=True, methods=['get'], url_path='share')
    def share(self, request, **kwargs):
        """Просмотр приглашённых пользователей <DOC_TYPE>/<id>/share/"""
        user = request.user
        obj = self.get_object()
        model_name = self.basename
        ct = ContentType.objects.get(model=model_name)
        # Фильтр по объекту
        up_qs = UserPermission.objects \
            .filter(object_id=kwargs['pk']) \
            .filter(content_type_id=ct)\
            .exclude(user_id__is_active=False)
        print(34, up_qs)
        ls = []
        if up_qs:
            for up in up_qs:
                # Конвертируем разрешения в строковый вид
                sh_perm_str = PERMS.as_string_list(up.permission)
                # получаем имя пользователя
                name = " ".join([up.user.first_name, up.user.last_name])
                ls.append({"email": up.user.email,
                           "perm": sh_perm_str[0],
                           "in_project": up.user.is_verified,
                           "datetime": int(up.datetime.timestamp()),
                           "name": name.strip()})

        return Response({'invites': ls})

    @action(detail=True, methods=['patch'], url_path='share/add')
    def add(self, request, **kwargs):
        """Добавление приглашённых пользователей <DOC_TYPE>/<id>/share/add/"""
        data = dict(request.data)
        obj = self.get_object()
        message = data.get('message', '')

        if 'email' not in data:
            raise ValidationError({"error": {"email": "field required"}})
        invite_email = data['email'].lower()

        try:
            validate_email(invite_email)
        except django.core.exceptions.ValidationError:
            raise ValidationError({"error": "incorrect email"})

        invite_user = User.objects.filter(email=invite_email).first()
        user_does_not_exist = True if not invite_user else False

        if 'perm' not in data:
            raise ValidationError({"error": {"perm": "field required"}})
        perm = data['perm']
        # if not isinstance(perms, list):
        #     raise ValidationError({"error": {"perms": "list of str"}})

        if perm not in permissions:
            raise ValidationError(
                {"error": {"perm": f"choices: {permissions}"}})

        # если юзер не собственник, но пытается дать кому-то собственника, то ошибка
        if request.user != obj.owner and perm == 'own':
            return Response({"error": "you can not change owner permission"},
                            status=status.HTTP_403_FORBIDDEN)

        # если юзер не собственник, но пытается изменить роль собственника, то ошибка
        if invite_email == obj.owner.email:
            return Response({"error": "you can not change owner permission"},
                            status=status.HTTP_403_FORBIDDEN)

        # если юзер пытается поменять свои права, то ошибка
        if request.user.email == invite_email:
            return Response({"error": "you can not change permission for yourself"},
                            status=status.HTTP_403_FORBIDDEN)

        # Есть-ли аккаунт у юзера
        # TODO Реализовать проверку регистрации пользователя по приглашению и
        # выдать ему доступ к документу
        if user_does_not_exist or not invite_user.is_verified:
            email_body = f'Вам предоставлен доступ к документу "{obj.name}".\n' \
                         f'Автор: {obj.owner} ({obj.owner.email})\n' \
                         f'Ссылка:  https://{ALLOWED_HOSTS[0]}/registry?email={invite_email}/'\
                         f'\n{message}'
            email = EmailMessage('Приглашение зарегистрироваться',
                                 email_body, to=[invite_email])
            email.send()

            if not invite_user:
                invite_user = User.objects.create(email=invite_email)
                invite_user.set_password(str(invite_email))
            invite_user.set_object_perm(obj, perm)
            if perm == 'own':
                obj.owner = invite_user
                obj.save()
            invite_user.save()

        # Если у юзера пока нет допуска к документу, выдаём разрешения
        elif not invite_user.has_any_object_perm(obj, permissions):
            email_body = f'Вам предоставлен доступ к документу "{obj.name}". ' \
                         f'\nАвтор: {obj.owner} ({obj.owner.email})' \
                         f'\nВыданы права: {perm}'\
                         f'\n{message}'
            email = EmailMessage('Приглашение', email_body, to=[invite_email])
            email.send()
            invite_user.grant_object_perm(obj, perm)
            if perm == 'own':
                obj.owner = invite_user
                request.user.set_object_perm(obj, 'edit')
                obj.save()

        # Если у юзера есть допуск к документу, удаляем старые разрешения,
        # выдаём только те что в новом запросе
        elif invite_user.has_any_object_perm(obj, ['read', 'edit']):
            email_body = f'Доступ к документу "{obj.name}" изменён. ' \
                         f'\nАвтор: {obj.owner} ({obj.owner.email})' \
                         f'\nВыданы права: {perm}' \
                         f'\n{message}'
            email = EmailMessage('Приглашение', email_body, to=[invite_email])
            email.send()
            invite_user.set_object_perm(obj, perm)
            if perm == 'own':
                obj.owner = invite_user
                request.user.set_object_perm(obj, 'edit')
                obj.save()

        else:
            Response({"success": f"Registration info sent to {invite_email}"},
                     status=status.HTTP_201_CREATED)

        data = {'email': invite_email,
                'perm': perm,
                'date': int(datetime.datetime.now().timestamp()),
                'in_project': invite_user.is_verified}

        # если юзер был зарегистрирован, получаем его имя и фамилию
        if not user_does_not_exist and invite_user.is_verified:
            name = " ".join([invite_user.first_name, invite_user.last_name])
            data.update({"name": name.strip()})

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='share/del')
    def trash(self, request, **kwargs):
        """Удаление приглашённого пользователя <DOC_TYPE>/<id>/share/del/"""
        req_data = dict(request.data)
        if 'email' not in req_data:
            raise ValidationError({"error": {"email": "field required"}})

        user_email = req_data['email']
        try:
            user = User.objects.get(email=user_email)
        except ObjectDoesNotExist:
            raise ValidationError({"error": {"email": "user not found"}})
        obj = self.get_object()
        if user.email == obj.owner.email:
            return Response({"error": {"email": "owner can not be removed"}},
                            status=status.HTTP_403_FORBIDDEN)
        # читатель может только выйти из проекта
        if request.user.has_object_perm(obj, ['read']) and user.email != request.user.email:
            return Response({"error": {"permission": "reader can't remove anybody except themselves"}},
                            status=status.HTTP_403_FORBIDDEN)

        if user.has_object_perm(obj, ['read', 'edit']):
            user.revoke_all_object_perm(obj)
            return Response({"success": f"{user} removed from {obj}"})
        return Response({"error": f"{user} have no permissions to {obj}"},
                        status=status.HTTP_403_FORBIDDEN)
