from django.urls import path, re_path

from . import consumers


urlpatterns = [
    path("<slug:bordimatic_pk>", consumers.JobUserConsumer.as_asgi()),
]
