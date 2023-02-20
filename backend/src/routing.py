from django.urls import path
from graphql_utils.routing import urlpatterns as graphql_urlpatterns
from channels.routing import URLRouter

#from . import consumers

websocket_urlpatterns = [
    path('ws/graphql/', URLRouter(graphql_urlpatterns)),
]
