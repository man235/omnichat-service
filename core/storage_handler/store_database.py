from typing import Dict
from core.schema import CoreChatInputMessage, NatsChatMessage
from core import constants
from core.handlers import BaseHandler
from core.utils import format_receive_message, save_message_store_databases
from sop_chat_service.zalo.utils import save_message_store_database_zalo
class StorageDataBase(BaseHandler):
    storage_type = constants.STORAGE_DATABASE

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):            
        message_storage = format_receive_message(data)
        
        if data.typeChat == 'facebook':
            await save_message_store_databases(room, message_storage)
        elif data.typeChat == 'zalo':
            await save_message_store_database_zalo(room, message_storage)
