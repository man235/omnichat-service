from .base import BaseAppContext
from core.abstractions import SingletonClass

class AppContextManager(BaseAppContext, SingletonClass):
    def _singleton_init(self, **kwargs):
        self._test = "Test AppContextManager"
