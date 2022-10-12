from core.abstractions.handler_abs import AbsHandler
from core.schema import CoreChatInputMessage
from core import constants
from core.handlers import BaseHandler
from typing import Dict


class StorageRedis(BaseHandler):
    storage_type = constants.STORAGE_REDIS

    async def handle_message(self, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        pass
