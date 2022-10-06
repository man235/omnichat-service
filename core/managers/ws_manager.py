from .base import BaseManager
from core import constants
from typing import Dict
from core.schema import CoreChatInputMessage
from core.websocket_handler import FacebookWebSocketHandler, LiveChatWebSocketHandler
from core.abstractions import AbsHandler



class WebSocketManager(BaseManager):
    manager_type: str = constants.WEBSOCKET_MANAGER
    ws_type: str = None

    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        for handler_class in (FacebookWebSocketHandler,LiveChatWebSocketHandler):
            handler_instance = handler_class()
            await handler_instance.set_manager(self)
            self._handlers.update({handler_instance.ws_type: handler_instance})
        return self._handlers

    async def process_message(self, room, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        handler: AbsHandler = self._handlers.get(message.chat_type)
        if handler:
            await handler.handle_message(room, message, data, **kwargs)
        else:
            print(f'{self.__class__.__name__} not found handler for {message}')
