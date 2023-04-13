from rest_framework.exceptions import PermissionDenied

from folders.models import Folder


class PermissionClass:

    @classmethod
    def has_permission(cls, info):
        user = info.context.user
        if not user:
            raise PermissionDenied({'error': 'you are not authenticated'})
        if user.is_invited:
            return user

        # Временное отключение требования к подписке
        # subs_end = user.subscription.end_datetime
        # if subs_end.astimezone(tz=timezone.utc) < timezone.now():
        #     raise PermissionDenied({'error': 'you subscription is over'})
        return user

    @classmethod
    def has_query_object_permission(cls, info, instance):

        user = info.context.user
        if not user.has_object_perm(instance, ['read', 'edit', 'own']) and not user.is_invited:
            folder = instance.parent_folder if isinstance(instance, Folder) else instance.folder
            while folder:
                if user.has_object_perm(folder, ['read', 'edit', 'own']):
                    break
                folder = folder.parent_folder
            if not folder:
                raise PermissionDenied(
                    {'error': f'You don`t have access to this object: {instance}'})

    @classmethod
    def has_mutate_object_permission(cls, info, instance):

        user = info.context.user
        if not user.has_object_perm(instance, ['edit', 'own']) and not user.is_invited:
            folder = instance.parent_folder if isinstance(instance, Folder) else instance.folder
            while folder:
                if user.has_object_perm(folder, ['edit', 'own']):
                    break
                folder = folder.parent_folder
            if not folder:
                raise PermissionDenied(
                    {'error': f'You don`t have access to this object: {instance}'})
