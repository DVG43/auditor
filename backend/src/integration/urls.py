from django.urls import include, path
from rest_framework import routers

from integration.views.googlesheet import GoogleSheetIntegrationViewSet, CreateGoogleSheetView
from integration.views.allintegrationsisactive import AllIntegrationsIsActiveView

# from integration.views.googleauth_views import (RedirectToGoogleAuthView,
#                                               GetGoogleTokensView)

all_integrations_endpoints = [
    path('<int:pk>/checkisactive/', AllIntegrationsIsActiveView.as_view()), ]

google_auth_endpoints = [
    #    path('', RedirectToGoogleAuthView.as_view()),
    #    path('getgoogletokens/', GetGoogleTokensView.as_view()),
    path('creategooglesheet/', CreateGoogleSheetView.as_view())
]
