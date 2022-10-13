# from .base import BaseWebSocketHandler
from core import constants
from core.schema import FormatSendMessage
from core.handlers import BaseHandler
import logging
from core.utils import format_receive_message


logger = logging.getLogger(__name__)

class SendMessageWebSocketHandler(BaseHandler):
    send_message_type: str = constants.SEND_MESSAGE_WEBSOCKET

    async def handle_message(self, room, message: FormatSendMessage, *args, **kwargs):
        new_topic_publish = f'{constants.CORECHAT_TO_WEBHOOK_FACEBOOK}.{room.room_id}'
        data_ws = message.json().encode()
        await self.manager.nats_client.publish(new_topic_publish, data_ws)
        logger.debug(f"{new_topic_publish} ------ {message.uuid}")
