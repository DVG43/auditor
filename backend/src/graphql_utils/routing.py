from django.urls import path
from .consumers import MyGraphqlWsConsumer

urlpatterns = [
    path("", MyGraphqlWsConsumer.as_asgi()),
]
