# from .base import BaseWebSocketHandler
from core.utils import format_receive_message
from core import constants
from core.schema import CoreChatInputMessage, NatsChatMessage
from core.handlers import BaseHandler
from typing import Dict
import logging
logger = logging.getLogger(__name__)


class ZaloWebSocketHandler(BaseHandler):
    ws_type: str = constants.ZALO

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):
        message_ws = format_receive_message(data)
        data_ws = message_ws.json().encode()
        await self.manager.nats_client.publish_message_from_corechat_to_websocket_zalo(room_id = room.room_id, payload = data_ws)
