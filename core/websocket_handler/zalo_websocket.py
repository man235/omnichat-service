# from .base import BaseWebSocketHandler
from core.utils import format_receive_message_to_websocket
from core import constants
from core.schema import NatsChatMessage
from core.handlers import BaseHandler
from sop_chat_service.zalo.utils.chat_support.format_message_zalo import format_atachment_type_from_zalo_message
import logging

logger = logging.getLogger(__name__)


class ZaloWebSocketHandler(BaseHandler):
    ws_type: str = constants.ZALO

    async def handle_message(self, room, data: NatsChatMessage, *args, **kwargs):
        # format attachment type
        if data.attachments:
            optionals = data.optionals
            for index, attachment in enumerate(data.attachments):
                if optionals[index] and optionals[index].data.get('attachments'):
                    data.attachments[index].type, \
                    data.attachments[index].name, \
                    data.attachments[index].size, \
                    attachment_id = format_atachment_type_from_zalo_message(attachment, optionals, index)
                
        message_ws = format_receive_message_to_websocket(room, data)
        data_ws = message_ws.json().encode()
        await self.manager.nats_client.publish_message_from_corechat_to_websocket_zalo(room_id = room.room_id, payload = data_ws)
