from django.db.models import Q
from typing import List

from folders.models import Folder
from objectpermissions.models import UserPermission


def get_child_folders(child_folders) -> List:
    folders = []
    for folder in child_folders:
        folders.append(folder)
        new_child_folders = folder.folders.all()
        if new_child_folders:
            folders.extend(get_child_folders(new_child_folders))
    return folders


def get_user_folders_own_or_with_perm(request) -> List[Folder]:
    q_own_folders = Q(owner=request.user, parent_folder=None)
    objects = UserPermission.objects.filter(
        user=request.user,
        content_type__model='folder'
    ).exclude(permission=4)
    folders_perms_id = []
    for object in objects:
        folders_perms_id.append(object.object_id)
    folders = Folder.objects.filter(q_own_folders | Q(id__in=folders_perms_id))
    return folders
