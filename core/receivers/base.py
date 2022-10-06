from typing import Dict
from core.abstractions import (
    AbsAppContext,
    SingletonClass,
    AbsRouter,
    AbsReceive
)

class BaseReceiver(AbsReceive, SingletonClass):
    def _singleton_init(self, **kwargs):
        self._initialized: bool = False
        self._routers: Dict[str, AbsRouter] = {}

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context

    async def receiver_message(self, *args, **kwargs):
        pass
