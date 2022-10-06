# from .base import BaseWebSocketHandler
from core import constants
from core.schema import CoreChatInputMessage
from core.handlers import BaseHandler
from typing import Dict
import logging
logger = logging.getLogger(__name__)


class ZaloWebSocketHandler(BaseHandler):
    ws_type: str = constants.ZALO

    async def handle_message(self, room, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        new_topic_publish = f'message_{room.room_id}'
        await self.manager.nats_client.publish(new_topic_publish, data.encode())
        logger.debug(f"{new_topic_publish} ------ {data['uuid']}")
