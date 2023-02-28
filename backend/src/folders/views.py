from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import PpmViewSet
from folders.models import Folder
from folders.serializers import\
    FolderSerializer,\
    FolderListSerializer
from shared_access.mixins import ShareMixin
from shared_access.serializers import\
    ShareFolderSerializer,\
    ShareDeleteSerializer
from objectpermissions.models import UserPermission


class FolderViewSet(PpmViewSet, ShareMixin):
    queryset = Folder.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list':
            return FolderListSerializer
        elif self.action == "add":
            return ShareFolderSerializer
        elif self.action == "trash":
            return ShareDeleteSerializer
        else:
            return FolderSerializer

    @action(methods=["GET"], detail=False, url_path='tree')
    def get_folders_tree(self, request):
        q_own_folders = Q(owner=request.user, parent_folder=None)
        objects = UserPermission.objects.filter(
            user=request.user,
            content_type__model='folder'
        ).exclude(permission=4)
        folders_perms_id = []
        for object in objects:
            folders_perms_id.append(object.object_id)
        folders = Folder.objects.filter(q_own_folders | Q(id__in=folders_perms_id))
        serializer = self.get_serializer(folders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
