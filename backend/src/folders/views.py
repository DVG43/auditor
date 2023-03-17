from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import PpmViewSet
from folders.models import Folder
from folders.utils import get_user_folders_own_or_with_perm
from folders.serializers import\
    FolderSerializer,\
    FolderListSerializer
from shared_access.mixins import ShareMixin
from shared_access.serializers import\
    ShareFolderSerializer,\
    ShareDeleteSerializer


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
        folders = get_user_folders_own_or_with_perm(request)
        serializer = self.get_serializer(folders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
