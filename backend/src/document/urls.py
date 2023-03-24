from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from document.views import (
    ChangeDocumentLogoView,
    DicumentViewSet,
    ProjectViewSet,
    ImageGeneration,
)
import document.views as views


urlpatterns = [
    path('folders/document/<int:pk>/', DicumentViewSet.as_view({'get': 'retrieve'})),
    path('folders/<int:pk>/document/', ProjectViewSet.as_view({'get': 'retrieve'})),
    path('projects/document-logo/<int:doc_pk>/', ChangeDocumentLogoView.as_view()),

    ## Image generation
    path('projects/document/image_generator/', ImageGeneration.as_view()),

    ## Text generation
    path('ai/theme_to_text/', views.ThemeToText.as_view()),
    path('ai/text_rephrase/', views.TextRephrase.as_view()),
    path('ai/text_shorter/', views.TextShorter.as_view()),
    path('ai/text_continue/', views.TextContinue.as_view()),
    path('ai/query_ai/', views.QueryAi.as_view()),
]
