from common.views import PpmViewSet
from folders.models import Folder
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

