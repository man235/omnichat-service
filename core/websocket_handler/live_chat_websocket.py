# from .base import BaseWebSocketHandler
from typing import Dict
from core import constants
from core.schema import CoreChatInputMessage
from core.handlers import BaseHandler
import logging

from core.schema.message_receive import NatsChatMessage
from core.utils.format_message_for_websocket import format_receive_live_chat
logger = logging.getLogger(__name__)


class LiveChatWebSocketHandler(BaseHandler):
    ws_type: str = constants.LIVECHAT
    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):
        new_topic_publish = f'LiveChat.SaleMan.{room.room_id}'
        message_ws = format_receive_live_chat(data)
        data_ws = message_ws.json().encode()
        await self.manager.nats_client.publish(new_topic_publish, data_ws)
        logger.debug(f"{new_topic_publish} ------ ****************************************** ")

        # # print(data)
        # logger.debug(f"{new_topic_publish} ------ {data['uuid']}")
        
    async def room_events(self,user_id, room, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        new_topic_publish = f'live-chat-action-room.{user_id}'
        message_ws = format_receive_live_chat(data)
        data_ws = message_ws.json().encode()
        await self.manager.nats_client.publish(new_topic_publish, data_ws)
        logger.debug(f"{new_topic_publish} ------ {data['uuid']}")
