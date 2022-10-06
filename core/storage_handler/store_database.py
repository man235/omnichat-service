from typing import Dict
from core.schema import CoreChatInputMessage, NatsChatMessage
from core import constants
from core.handlers import BaseHandler
from core.utils import format_receive_message, save_message_store_databases


class StorageDataBase(BaseHandler):
    storage_type = constants.STORAGE_DATABASE

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):
        message_storage = format_receive_message(data)
        await save_message_store_databases(room, message_storage)
