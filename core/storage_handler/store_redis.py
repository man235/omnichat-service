from core import constants
from core.handlers import BaseHandler
from core.schema import NatsChatMessage
from typing import Dict


class StorageRedis(BaseHandler):
    storage_type = constants.STORAGE_REDIS

    async def handle_message(self, room, data: NatsChatMessage, *args, **kwargs):
        redis_client = self.manager.context.redis_client
        redis_client.hset(f'{constants.REDIS_LAST_MESSAGE_ROOM}{room.room_id}', constants.LAST_MESSAGE, data.timestamp)
