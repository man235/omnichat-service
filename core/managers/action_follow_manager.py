from typing import Dict
from .base import BaseManager
from core import constants
from core.schema import FormatSendMessage
from core.abstractions import AbsHandler
from core.action_handler import ActionFollowHandler
from sop_chat_service.app_connect.models import Room


class ActionFollowManager(BaseManager):
    manager_type: str = constants.ACTION_FOLLOW_MANAGER

    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        for handler_class in (ActionFollowHandler, ):
            handler_instance = handler_class()
            await handler_instance.set_manager(self)
            self._handlers.update({handler_instance.send_message_type: handler_instance})
        return self._handlers

    async def process_message(self, message: FormatSendMessage, *args, **kwargs):
        room =  Room.objects.filter(room_id=message.room_id).first()
        action_handler: AbsHandler = self._handlers.get(constants.ACTION_FOLLOW_HANDLER)
        await action_handler.handle_message(room, message)
