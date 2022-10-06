# from .base import BaseWebSocketHandler
from core import constants
from core.schema import CoreChatInputMessage
from core.handlers import BaseHandler
from typing import Dict

class FacebookWebSocketHandler(BaseHandler):
    ws_type: str = constants.FACEBOOK

    async def handle_message(self, room, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        new_topic_publish = f'message_{room.room_id}'
        await self.manager.nats_client.publish(new_topic_publish, data.encode())
        await self.manager.nats_client.publish("thienhi", data.encode())
