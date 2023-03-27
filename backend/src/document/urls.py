from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from document.views import (
    ChangeDocumentLogoView,
    DicumentViewSet,
    ProjectViewSet,
    ImageGeneration,
    Text2Speech,
)


urlpatterns = [
    path('folders/document/<int:pk>/', DicumentViewSet.as_view({'get': 'retrieve'})),
    path('folders/<int:pk>/document/', ProjectViewSet.as_view({'get': 'retrieve'})),
    path('projects/document-logo/<int:doc_pk>/', ChangeDocumentLogoView.as_view()),

    ## Image generation
    path('projects/document/image_generator/', ImageGeneration.as_view()),
    ## Text to speech
    path('projects/document/text2speech/<int:pk>/', Text2Speech.as_view()),
]
