# from .base import BaseWebSocketHandler
from core import constants
from core.schema import FormatSendMessage
from core.handlers import BaseHandler
import logging


logger = logging.getLogger(__name__)

class MessageLogWebSocketHandler(BaseHandler):
    send_message_type: str = constants.MESSAGE_LOG_WEBSOCKET

    async def handle_message(self, room, message: FormatSendMessage, *args, **kwargs):
        data_ws = message.json().encode()
        if message.type == 'facebook':
            new_topic_publish = f'{constants.CORECHAT_TO_WEBSOCKET_FACEBOOK}.{room.room_id}'
        elif message.type == 'zalo':
            new_topic_publish = f'{constants.CORECHAT_TO_WEBSOCKET_ZALO}.{room.room_id}'
        await self.manager.nats_client.publish(new_topic_publish, data_ws)
        logger.debug(f"{new_topic_publish} ------ {message.uuid}")
