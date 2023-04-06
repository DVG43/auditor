from django.urls import path
from . import views


urlpatterns = [
    # path('ai/theme_to_text/', views.ThemeToText.as_view()),
    # path('ai/text_rephrase/', views.TextRephrase.as_view()),
    # path('ai/text_shorter/', views.TextShorter.as_view()),
    # path('ai/text_continue/', views.TextContinue.as_view()),
    path('ai/query_ai/', views.QueryAi.as_view()),
    path('ai/standard_generation/', views.StandardGeneration.as_view()),
]
