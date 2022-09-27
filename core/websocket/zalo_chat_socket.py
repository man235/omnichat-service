import json
from django.conf import settings
from nats.aio.client import Client as NATS
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
import logging
logger = logging.getLogger(__name__)


nats_client = NATS()
class ZaloChatConsumer(AsyncJsonWebsocketConsumer):
    async def subscribe_handler(self, msg):
        # data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
        logger.debug(f'data subscribe natsUrl ----------------- {msg.data.decode("utf-8")}')
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',     # call func chat_message handler
                'message': msg.data.decode("utf-8")
            }
        )

    async def connect(self):
        """
        Connect to socket channels
        Connect to nats servers then make a subscription
        """
        # Get data of `request` object captured by middleware
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        self.room_group_name = f'{self.topic}_{self.room_id}'
        await nats_client.connect(
            servers=[settings.NATS_URL]
        )
        #
        sub = await nats_client.subscribe(self.room_group_name, self.room_group_name, cb = self.subscribe_handler)
        # To can be accessed over other methods
        self.sub = sub
        # Take a `channel_name` channel and add it into `room_group_name` group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.sub.unsubscribe()
        await nats_client.close()

    async def receive(self, text_data):
        logger.debug(f'receive data websocket ----------------- ===============')
        data = json.loads(text_data)
        logger.info(f'data received from websocket ---------- {data}')
        pass

    async def chat_message(self, event):
        message = event['message']
        # await self.send_json({
        #     "data": message,
        # })
        await self.send(text_data=message)
    
    @sync_to_async
    def save_message(self, username, room, message):
        """
        Create `Message` model
        """
        