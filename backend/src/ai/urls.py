from pathlib import Path
from django.http import HttpResponse
from django.urls import path
from . import views

TEST_EVENTSOURCE_PAGE_HTML = Path('./ai/test_eventsource.html').read_text()
TEST_FETCH_PAGE_HTML = Path('./ai/test_fetch.html').read_text()

def get_test_eventsource_page(request):
    return HttpResponse(TEST_EVENTSOURCE_PAGE_HTML)

def get_test_fetch_page(request):
    return HttpResponse(TEST_FETCH_PAGE_HTML)

urlpatterns = [
    # path('ai/theme_to_text/', views.ThemeToText.as_view()),
    # path('ai/text_rephrase/', views.TextRephrase.as_view()),
    # path('ai/text_shorter/', views.TextShorter.as_view()),
    # path('ai/text_continue/', views.TextContinue.as_view()),
    path('ai/query_ai/', views.QueryAi.as_view()),
    path('ai/standard_generation/', views.StandardGeneration.as_view()),

    path('test_eventsource.html', get_test_eventsource_page),
    path('test_fetch.html', get_test_fetch_page),

    path('stream/ai/test/', views.StreamTest.as_view()),
    path('stream/ai/query_ai/', views.QueryAiStream.as_view()),
    path('stream/ai/standard_generation/',
       views.StandardGenerationStream.as_view()),
]
