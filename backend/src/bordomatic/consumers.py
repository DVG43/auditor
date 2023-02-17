# import json
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

import json
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import BordomaticPrivate


class JobUserConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        '''
        Creates group, add to the valid channels
        Connects and sends to the browser the last jobs
        '''
        user = self.scope["user"]
        self.group_name = self.scope['url_route']['kwargs']['bordimatic_pk']

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data = json.dumps({"status": "websocket.accept",}))

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_message(self, event):
        message = event['text']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(
            message
        ))

