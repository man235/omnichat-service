from .base import BaseAppContext
from core.abstractions import SingletonClass
from core.stream.redis_connection import redis_client


class AppContextManager(BaseAppContext, SingletonClass):
    def _singleton_init(self, **kwargs):
        self._test = "Test AppContextManager"
        self.redis_client = redis_client
