from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from common.utils import find_host_project, unpack_nested_kwargs, get_model


class IsOwner(BasePermission):
    def has_permission(self, request, view):

        ### Временное отключение требования к подписке
        # subs_end = request.user.subscription.end_datetime
        # if subs_end.astimezone(tz=timezone.utc) < timezone.now():
        #     raise PermissionDenied({'error': 'you subscription is over'})
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # request.user.has_object_perm(obj, 'own')
        if not obj.owner == request.user:
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})
        return obj.owner == request.user


class IsOwnerOrIsInvited(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_invited:
            return True

        ### Временное отключение требования к подписке
        # subs_end = request.user.subscription.end_datetime
        # if subs_end.astimezone(tz=timezone.utc) < timezone.now():
        #     raise PermissionDenied({'error': 'you subscription is over'})
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # request.user.has_object_perm(obj, 'own')
        if request.user.is_invited:
            if obj.doc_uuid != request.user.document:
                raise PermissionDenied(
                    {'error': 'You don`t have access to this object'})
            return obj.doc_uuid == request.user.document

        if not obj.owner == request.user:
            raise PermissionDenied(
                {'error': 'You don`t have access to this object'})
        return obj.owner == request.user


class IsOwnerOrIsProjectAccess(BasePermission):
    """Проверка доступа к проекту или к директории проекта"""

    def has_permission(self, request, view):
        kw = unpack_nested_kwargs(view.kwargs, view.basename)

        # если пользователь является пользователем по ссылке, то мы его пропускаем
        if not isinstance(request.user, AnonymousUser):
            if request.user.is_invited:
                return True

        # проверяем доступ редактора при создании документа в директории или проекте
        if view.action == "create" and view.basename != 'project':
            folder = None
            if 'folder' in request.data:
                folder = get_model('folder').objects.filter(id=request.data['folder'])[0]
            while folder:
                if request.user.has_object_perm(folder, ['edit', 'own']):
                    break
                else:
                    folder = folder.parent_folder
            if not folder:
                obj = find_host_project(kw)
                if obj:
                    if not request.user.has_object_perm(obj, ['edit', 'own']):
                        raise PermissionDenied(
                            {'error': 'You don`t have access to this object'})
                else:
                    raise PermissionDenied(
                        {'error': 'You don`t have access to this object'})

        # проверяем подписку
        ### Временное отключение требования к подписке
        # subs_end = request.user.subscription.end_datetime \
        #     if hasattr(request.user, 'subscription') else None
        # if subs_end is not None and subs_end.astimezone(tz=timezone.utc) < timezone.now():
        #     raise PermissionDenied({'error': 'you subscription is over'})
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        # если пользователь является собственником, то у него есть любы права на любой объект
        if obj.owner == request.user:
            return True

        # если мы проверяем доступ к вложенному документу
        # проекта неприглашенного по ссылке пользователя,
        # ищем сначала директорию с открытым доступом
        # если директории нету, то проект с открытым доступом


        if view.basename != 'project' and not request.user.is_invited:
            if view.basename == 'folder':
                folder = obj
            else:
                folder = obj.folder
            while folder:
                if request.user.has_object_perm(folder, ['read', 'edit', 'own']):
                    obj = folder
                    break
                else:
                    folder = folder.parent_folder
            if not folder:
                obj = find_host_project(view.kw)
            if obj.owner == request.user:
                return True

        # чтение и выход из проекта доступны и редакторам, и читателям
        if view.action in ["list", "retrieve", "share", "trash"] and \
            request.user.has_object_perm(obj, ['read', 'edit', 'own']):
            return True

        # обновление, добавление контактов в проект и их удаление из проекта,
        # перемещение и копирование документов между проектами
        #  доступно только редактору и собственнику
        if view.action in ["update", "partial_update", "add", "move_document",
                           "copy_document"] and \
            request.user.has_object_perm(obj, ['edit', 'own']):
            return True

        # удаление документов из проекта доступно редактору и собственнику
        if view.action == "destroy" and \
            view.basename != "project" and \
            request.user.has_object_perm(obj, ['edit']):
            return True
        raise PermissionDenied(
            {'error': 'You don`t have access to this object'})

# def media_access(request, path):
#     user = request.user
#     file_name = path.split('/')[0]
#     file = UserFile.objects.get(file=file_name)
#
#     token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
#     try:
#         valid_data = TokenBackend(
#             algorithm='HS256', signing_key=settings.SECRET_KEY)\
#             .decode(token, verify=True)
#         user_id = valid_data['user_id']
#         user = User.objects.get(id=user_id)
#         request.user = user
#     except ValidationError as v:
#         print("validation error", v)
#
#     if user.has_any_object_perm(file, 'own'):
#         response = HttpResponse()
#         del response['Content-Type']
#         response['X-Accel-Redirect'] = '/media/' + path
#         return response
#     else:
#         return HttpResponseForbidden('Not authorized to access this media.')
