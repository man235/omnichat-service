from typing import Dict
from core import constants
from core.handlers import BaseHandler
from core.schema import FormatSendMessage
from core.utils import facebook_send_message_store_database, zalo_send_message_store_database


class SendMessageStorageHandler(BaseHandler):
    send_message_type = constants.SEND_MESSAGE_STORAGE_DATABASE

    async def handle_message(self, room, message: FormatSendMessage, *args, **kwargs):
        if message.type == constants.FACEBOOK:
            await facebook_send_message_store_database(room, message)
        # if message.type == constants.ZALO:
        #     await zalo_send_message_store_database(room, message)
        