from pathlib import Path
from django.http import HttpResponse
from django.urls import path
from . import views

# TEST_PAGE_HTML = Path('./ai/test_page.html').read_text()

# def get_test_page(request):
#     return HttpResponse(TEST_PAGE_HTML)

urlpatterns = [
    # path('ai/theme_to_text/', views.ThemeToText.as_view()),
    # path('ai/text_rephrase/', views.TextRephrase.as_view()),
    # path('ai/text_shorter/', views.TextShorter.as_view()),
    # path('ai/text_continue/', views.TextContinue.as_view()),
    path('ai/query_ai/', views.QueryAi.as_view()),
    path('ai/standard_generation/', views.StandardGeneration.as_view()),
    path('stream_test/', views.StreamTest.as_view()),
    # path('test_page.html', get_test_page),
]
