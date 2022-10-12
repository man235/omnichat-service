# from .base import BaseWebSocketHandler
from core import constants
from core.schema import CoreChatInputMessage, NatsChatMessage
from core.handlers import BaseHandler
import logging
from core.utils import format_receive_message


logger = logging.getLogger(__name__)

class FacebookWebSocketHandler(BaseHandler):
    ws_type: str = constants.FACEBOOK

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):
        new_topic_publish = f'message_{room.room_id}'
        message_ws = format_receive_message(data)
        data_ws = message_ws.json().encode()
        await self.manager.nats_client.publish(new_topic_publish, data_ws)
        logger.debug(f"{new_topic_publish} ------ {data.uuid}")
