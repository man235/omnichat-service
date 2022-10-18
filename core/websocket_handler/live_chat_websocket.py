# from .base import BaseWebSocketHandler
from typing import Dict
from core import constants
from core.schema import CoreChatInputMessage
from core.handlers import BaseHandler
import logging

from core.schema.message_receive import NatsChatMessage
from core.utils.format_message_for_websocket import livechat_format_message_from_corechat_to_websocket, livechat_format_message_from_corechat_to_webhook
logger = logging.getLogger(__name__)


class LiveChatWebSocketHandler(BaseHandler):
    ws_type: str = constants.LIVECHAT

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):
        message_corechat_ws = livechat_format_message_from_corechat_to_websocket(room, data, constants.SIO_EVENT_NEW_MSG_CUSTOMER_TO_SALEMAN, False)
        message_corechat_webhook = livechat_format_message_from_corechat_to_webhook(room, data, constants.SIO_EVENT_ACK_MSG_CUSTOMER_TO_SALEMAN, True)
        # data_ws = message_corechat_ws.json().encode()
        
        await self.manager.nats_client.publish_message_from_corechat_to_websocket_livechat(
            room_id = room.room_id, payload = message_corechat_ws.json().encode()
        )
        await self.manager.nats_client.publish_message_from_corechat_to_webhook_livechat(
            room_id = room.room_id, payload = message_corechat_webhook.json().encode()
        )
        logger.debug(f"LiveChatWebSocketHandler ------ ****************************************** ")
