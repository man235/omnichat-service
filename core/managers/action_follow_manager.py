from typing import Dict
from .base import BaseManager
from core import constants
from core.schema import NatsChatMessage
from core.abstractions import AbsHandler
from core.action_handler import ActionFollowHandler


class ActionFollowManager(BaseManager):
    manager_type: str = constants.ACTION_FOLLOW_MANAGER

    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        for handler_class in (ActionFollowHandler, ):
            handler_instance = handler_class()
            await handler_instance.set_manager(self)
            self._handlers.update({handler_instance.send_message_type: handler_instance})
        return self._handlers

    async def process_message(self, room, message: NatsChatMessage, *args, **kwargs):
        action_handler: AbsHandler = self._handlers.get(constants.ACTION_FOLLOW_HANDLER)
        await action_handler.handle_message(None, message)
