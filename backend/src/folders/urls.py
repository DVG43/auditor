from django.urls import path, include
from rest_framework_nested import routers

from folders.views import (
    FolderViewSet
)
from urls import router


# projects/folders/
pr_folders_router = routers.NestedSimpleRouter(
    router, r'projects', lookup='project')
pr_folders_router.register(r'folders', FolderViewSet)


urlpatterns = [
    path('', include(pr_folders_router.urls))
]
