from typing import Dict
from .base import BaseManager
from core import constants
from core.schema import FormatSendMessage
from core.abstractions import AbsHandler
from core.send_message_handler import SendMessageStorageHandler, SendMessageWebSocketHandler
from sop_chat_service.app_connect.models import Room


class SendMessageManager(BaseManager):
    manager_type: str = constants.SEND_MESSAGE_MANAGER

    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        for handler_class in (SendMessageStorageHandler, SendMessageWebSocketHandler):
            handler_instance = handler_class()
            await handler_instance.set_manager(self)
            self._handlers.update({handler_instance.send_message_type: handler_instance})
        return self._handlers

    async def process_message(self, message: FormatSendMessage, *args, **kwargs):
        room =  Room.objects.filter(room_id=message.room_id).first()
        handler_ws: AbsHandler = self._handlers.get(constants.SEND_MESSAGE_WEBSOCKET)
        handler_storage: AbsHandler = self._handlers.get(constants.SEND_MESSAGE_STORAGE_DATABASE)
        # websocket handler
        await handler_ws.handle_message(room, message)
        # storage handler
        await handler_storage.handle_message(room, message)
