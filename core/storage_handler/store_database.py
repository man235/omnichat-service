from typing import Dict
from core.schema import CoreChatInputMessage
from core import constants
from core.handlers import BaseHandler
from core.utils import save_message_store_database


class StorageDataBase(BaseHandler):
    storage_type = constants.STORAGE_DATABASE

    async def handle_message(self, room, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        await save_message_store_database(room, data, data['_uuid'])
