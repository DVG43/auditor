import requests
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from django.core import files
from django.core.files.base import ContentFile
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone

from accounts.models import User
from graphql_utils import errors
from projects.models import Project
from folders.models import Folder


def jwt_decode(token, context=None):
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=["HS256"],
    )
    payload["email"] = get_user_model().objects.get(id=payload.get("user_id")).email
    return payload


class PermissionClass:

    @classmethod
    def has_permission(cls, info):
        user = info.context.user
        if not user:
            raise PermissionDenied({'error': 'you are not authenticated'})
        if user.is_invited:
            return user

        ### Временное отключение требования к подписке
        # subs_end = user.subscription.end_datetime
        # if subs_end.astimezone(tz=timezone.utc) < timezone.now():
        #     raise PermissionDenied({'error': 'you subscription is over'})
        return user

    @classmethod
    def has_query_object_permission(cls, info, prj_id):
        prj = Project.objects.filter(pk=prj_id).first()
        user = info.context.user
        if not user.has_object_perm(prj, ['read', 'edit', 'own']) and not user.is_invited:
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})

    @classmethod
    def has_mutate_object_permission(cls, info, prj_id):
        prj = Project.objects.filter(pk=prj_id).first()
        user = info.context.user
        if not user.has_object_perm(prj, ['edit', 'own']):
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})


class PermissionClassFolder(PermissionClass):

    @classmethod
    def has_query_object_permission(cls, info, folder_id):
        fold = Folder.objects.filter(pk=folder_id).first()
        user = info.context.user
        if not user.has_object_perm(fold, ['read', 'edit', 'own']) and not user.is_invited:
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})

    @classmethod
    def has_mutate_object_permission(cls, info, folder_id):
        fold = Folder.objects.filter(pk=folder_id).first()
        user = info.context.user
        if not user.has_object_perm(fold, ['edit', 'own']):
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})


def download_logo(url, project):
    # скачиваем логотип для документа по ссылке
    try:
        response = requests.get(url, allow_redirects=True)
    except (requests.HTTPError, requests.ConnectionError) as error:
        raise errors.WrongURLError({'document_logo_url': 'not valid url'})
    filename = url.split('/')[-1]
    file = files.File(ContentFile(response.content), filename)

    # проверяем достаточно ли места для скачиваемого файла на диске
    user = User.objects.filter(pkid=project.owner.pkid).first()
    disk_space = user.disk_space if user.disk_space else 0
    if file.size + disk_space > settings.DISK_SIZE:
        raise errors.NotEnoughSpaceError({'file': 'Not enough space on disk for file'})

    return files.File(ContentFile(response.content), filename)


def check_disk_space(project, info):
    user = project.owner
    disk_space = user.disk_space if user.disk_space else 0
    for filename, file in info.context.FILES.items():
        file_size = file.size
        if file_size + disk_space < settings.DISK_SIZE:
            disk_space += file_size
            return disk_space
    raise errors.NotEnoughSpaceError({'file': 'Not enough space on disk for file'})
