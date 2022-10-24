from typing import Dict
from core.schema import CoreChatInputMessage
from core import constants
from core.handlers import BaseHandler
from core.schema.message_receive import ChatOptional, NatsChatMessage
from core.utils import format_receive_message, format_receive_message_zalo, facebook_save_message_store_database
from core.utils.save_message_live_chat import live_chat_save_message_store_database
from sop_chat_service.zalo.utils import save_message_store_database_zalo, save_msg_store_database_zalo


class StorageDataBase(BaseHandler):
    storage_type = constants.STORAGE_DATABASE

    async def handle_message(self, room, message: CoreChatInputMessage, data: NatsChatMessage, *args, **kwargs):            
        # message_storage = format_receive_message(room, data)
        
        if data.typeChat == 'facebook':
            # await facebook_save_message_store_databases(room, message_storage)
            await facebook_save_message_store_database(room, data)
        elif data.typeChat == 'zalo':
            optionals: list[ChatOptional] = data.optionals
            msg_storages = format_receive_message_zalo(room, data)
            # for msg_storage in msg_storages:
                # await save_message_store_database_zalo(room, msg_storage, optionals)
            await save_msg_store_database_zalo(room, msg_storages[0], optionals)
        elif data.typeChat == "livechat":
            await live_chat_save_message_store_database(room,data)
        