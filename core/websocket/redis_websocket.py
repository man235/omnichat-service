import json
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class RedisFacebookChatConsumer(AsyncJsonWebsocketConsumer):
    async def subscribe_handler(self, msg):
        data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',     # call func chat_message handler
                'message': data
            }
        )

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'
        # channel.psubscribe(**{self.room_group_name: async_to_sync(self.subscribe_handler)})

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        for publish in channel.listen():
            pass

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def chat_message(self, event):
        message = event['message']
        await self.send_json({
            "data": message,
        })
