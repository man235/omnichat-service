import json
from core import constants
from django.conf import settings
from nats.aio.client import Client as NATS
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging
logger = logging.getLogger(__name__)


nats_client = NATS()
class FacebookChatConsumer(AsyncJsonWebsocketConsumer):
    async def subscribe_handler(self, msg):
        # data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
        logger.debug(f'data subscribe natsUrl ----------------- {msg.data.decode("utf-8")}')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',     # call func chat_message handler
                'message': msg.data.decode("utf-8")
            }
        )

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.topic = self.scope['url_route']['kwargs']['topic']
        user =self.scope['url_route']['kwargs']['x_auth_user_id']
        await nats_client.connect(
            servers=[settings.NATS_URL]
        )
        if self.topic == "live-chat-room" or self.topic == "live-chat-action-room":
            self.room_group_name = f'{self.topic}.{self.room_id}'

            # topics = [f'live-chat-room.{self.room_id}',f'live-chat-action-room.{user}']
            topics = [f'LiveChat.SaleMan.{self.room_id}',f'live-chat-action-room_{self.room_id}']
            for topic in topics:
                if topic == topics[0]:
                    sub = await nats_client.subscribe(topic, "message", self.subscribe_handler)
                if topic == topics[1]:
                    sub = await nats_client.subscribe(topic, "action_room", self.subscribe_handler)
            self.sub = sub
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
                
            )
            await self.accept()

        else:  
            # self.room_group_name = f'{self.topic}_{self.room_id}'
            self.room_group_name = f'{constants.CORECHAT_TO_WEBHOOK_FACEBOOK}.{self.room_id}'
            sub = await nats_client.subscribe(self.room_group_name, self.room_group_name, cb = self.subscribe_handler)
            self.sub = sub
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
        pass

    async def chat_message(self, event):
        message = event['message']
        # await self.send_json({
        #     "data": message,
        # })
        await self.send(message)
