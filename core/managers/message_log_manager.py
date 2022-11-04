from typing import Dict
from .base import BaseManager
from core import constants
from core.schema import FormatSendMessage
from core.abstractions import AbsHandler
from core.message_log_handler import MessageLogWebSocketHandler, MessageLogStorageHandler
from sop_chat_service.app_connect.models import Room


class MessageLogManager(BaseManager):
    manager_type: str = constants.MESSAGE_LOG_MANAGER

    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        for handler_class in (MessageLogWebSocketHandler, MessageLogStorageHandler):
            handler_instance = handler_class()
            await handler_instance.set_manager(self)
            self._handlers.update({handler_instance.send_message_type: handler_instance})
        return self._handlers

    async def process_message(self, message: FormatSendMessage, *args, **kwargs):
        room =  Room.objects.filter(room_id=message.room_id).first()
        msg_log_ws: AbsHandler = self._handlers.get(constants.MESSAGE_LOG_WEBSOCKET)
        msg_log_storage: AbsHandler = self._handlers.get(constants.MESSAGE_LOG_STORAGE_DATABASE)
        # websocket handler
        await msg_log_ws.handle_message(room, message)
        # storage handler
        await msg_log_storage.handle_message(room, message)
