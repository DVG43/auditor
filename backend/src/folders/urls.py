from django.urls import path, include
from rest_framework.routers import SimpleRouter

from folders.views import (
    FolderViewSet
)


# folders/
folders_router = SimpleRouter()
folders_router.register(r'folders', FolderViewSet)


urlpatterns = [
    path('', include(folders_router.urls))
]
