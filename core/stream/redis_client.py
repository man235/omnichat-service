# -*- coding: utf-8 -*-
from .sentinel import SentinelClient
from core.abstractions import SingletonClass

class RedisClient(SingletonClass):

    def _singleton_init(self, **kwargs):
        self._initialized()

    def reset_client(self):
        self._initialized()

    def _initialized(self, *args, **kwargs):
        self.client = SentinelClient()
        self.client.initialize_sentinel()

    async def add_test_redis(self, data, **kwargs) -> bool:
        keyT = f"add_test_redis"
        return await self.client.set(keyT, data)
