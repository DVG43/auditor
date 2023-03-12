from django.urls import include, path
from rest_framework import routers

from integration.views.googlesheet import GoogleSheetIntegrationViewSet, CreateGoogleSheetView
from integration.views.allintegrationsisactive import AllintegrationsIsActiveView
#from integration.views.googleauth_views import (RedirectToGoogleAuthView, 
#                                               GetGoogleTokensView)



router = routers.DefaultRouter()
router.register(r'googlesheetintegration', GoogleSheetIntegrationViewSet, 'googlesheetintegration')

all_integrations_endpoints = [
    path('<int:pk>/checkisactive/', AllintegrationsIsActiveView.as_view()),]

google_auth_endpoints = [
#    path('', RedirectToGoogleAuthView.as_view()),
#    path('getgoogletokens/', GetGoogleTokensView.as_view()),
    path('creategooglesheet/', CreateGoogleSheetView.as_view())
]
