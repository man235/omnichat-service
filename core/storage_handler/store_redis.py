from core import constants
from core.handlers import BaseHandler
from core.schema import NatsChatMessage
from typing import Dict


class StorageRedis(BaseHandler):
    storage_type = constants.STORAGE_REDIS

    async def handle_message(self, data: NatsChatMessage, *args, **kwargs):
        pass
