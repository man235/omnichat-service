from typing import Dict
from .base import BaseManager
from core import constants
from core.schema import NatsChatMessage
from core.abstractions import AbsHandler
from core.storage_handler import StorageDataBase, StorageRedis


class StorageManager(BaseManager):
    manager_type: str = constants.STORAGE_MANAGER

    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        for handler_class in (StorageDataBase,StorageRedis):
            handler_instance = handler_class()
            await handler_instance.set_manager(self)
            self._handlers.update({handler_instance.storage_type: handler_instance})
        return self._handlers

    async def process_message(self, room, data: NatsChatMessage, *args, **kwargs):
        handler: AbsHandler = self._handlers.get(constants.STORAGE_DATABASE)
        await handler.handle_message(room, data)

