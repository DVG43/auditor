
from django.contrib import admin
from django.urls import path

from .views import Tinkoff

urlpatterns = [
    path('tinkoff_pay/', Tinkoff.as_view(), name='tinkoff pay'),
]
