from typing import Dict
from core import constants
from core.handlers import BaseHandler
from core.schema import FormatSendMessage
from core.utils import storage_log_message


class MessageLogStorageHandler(BaseHandler):
    send_message_type = constants.MESSAGE_LOG_STORAGE_DATABASE

    async def handle_message(self, room, message: FormatSendMessage, *args, **kwargs):
        await storage_log_message(room, message)
        