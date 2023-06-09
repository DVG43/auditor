"""
ASGI config for src project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django_asgi_app = get_asgi_application() #я не знаю почему, но чтобы websocket работал оно должно быть именно здесь - до импортов )

from channels.security.websocket import AllowedHostsOriginValidator
from channelsmiddleware import JwtAuthMiddlewareStack

import routing

application = ProtocolTypeRouter({
  "http": django_asgi_app,
  "websocket": AllowedHostsOriginValidator(
          JwtAuthMiddlewareStack(       #надо передать параметр token в url веб сокета
            URLRouter(
                routing.websocket_urlpatterns
            )
        ),
    ),
})
