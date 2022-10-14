# from .base import BaseWebSocketHandler
from typing import Dict
from core import constants
from core.schema import CoreChatInputMessage
from core.handlers import BaseHandler
import logging

from core.schema.message_receive import NatsChatMessage
from core.utils.format_message_for_websocket import format_message_from_corechat_to_websocket, format_message_from_corechat_to_webhook
logger = logging.getLogger(__name__)


class LiveChatWebSocketHandler(BaseHandler):
    ws_type: str = constants.LIVECHAT

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):
        message_corechat_ws = format_message_from_corechat_to_websocket(room, data)
        message_corechat_webhook = format_message_from_corechat_to_webhook(room, data)
        # data_ws = message_corechat_ws.json().encode()
        await self.manager.nats_client.publish_message_from_corechat_to_websocket_livechat(room_id = room.room_id, payload = message_corechat_ws.json().encode())
        await self.manager.nats_client.publish_message_from_corechat_to_webhook_livechat(room_id = room.room_id, payload = message_corechat_webhook.json().encode())
        logger.debug(f"LiveChatWebSocketHandler ------ ****************************************** ")

    # async def room_events(self,user_id, room, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
    #     new_topic_publish = f'live-chat-action-room.{user_id}'
    #     message_ws = format_message_from_corechat_to_websocket(room, data)
    #     data_ws = message_ws.json().encode()
    #     await self.manager.nats_client.publish(new_topic_publish, data_ws)
    #     logger.debug(f"{new_topic_publish} ------ {data['uuid']}")
