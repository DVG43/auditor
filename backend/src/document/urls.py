from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from graphene_django.views import GraphQLView
from document.views import (
    ChangeDocumentLogoView,
    DicumentViewSet,
    ProjectViewSet,
    ImageGeneration,
    Text2Speech,
    EnableReadingAPIView,
    ReadConfirmationAPIView,
)


urlpatterns = [
    path('folders/document/<int:pk>/', DicumentViewSet.as_view({'get': 'retrieve'})),
    path('folders/<int:pk>/document/', ProjectViewSet.as_view({'get': 'retrieve'})),
    path('projects/document-logo/<int:doc_pk>/', ChangeDocumentLogoView.as_view()),
    path('document/confirm-reading/enabled/<int:pk>/', EnableReadingAPIView.as_view()),
    path('document/confirm-reading/users/<int:pk>/', ReadConfirmationAPIView.as_view()),

    ## Image generation
    path('projects/document/image_generator/', ImageGeneration.as_view()),

]
## Text to speech
if settings.YC_SPEECHKIT_ENABLED == True:
    urlpatterns += [path('projects/document/text2speech/<int:pk>/', Text2Speech.as_view())]
