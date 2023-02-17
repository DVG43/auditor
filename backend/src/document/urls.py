from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from document.views import ChangeDocumentLogoView, DicumentViewSet, ProjectViewSet


urlpatterns = [
    path('projects/document/<int:pk>/', DicumentViewSet.as_view({'get': 'retrieve'})),
    path('projects/<int:pk>/document/', ProjectViewSet.as_view({'get': 'retrieve'})),
    path('projects/document-logo/<int:doc_pk>/', ChangeDocumentLogoView.as_view())
]
