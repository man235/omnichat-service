from typing import Dict
from core.schema import CoreChatInputMessage
from core.abstractions import SingletonClass, AbsAppContext, AbsHandler, AbsManager
from core.stream import NatsClient


class BaseManager(SingletonClass, AbsManager):
    manager_type: str = None
    _handlers: Dict[str, AbsHandler] = {}

    async def initialize(self, *args, **kwargs):
        if self._initialized:
            return
        self._handlers = await self._get_handlers()
        self._initialized = True
        # if self._is_connected:
        #     return
        # self.nats_client = await self.nats_client.connect()
        await self.nats_client.connect()
        # self._is_connected = True

    def _singleton_init(self, **kwargs):
        self._initialized: bool = False
        self._is_connected: bool = False
        self._handlers: Dict[str, AbsHandler] = {}
        self.nats_client = NatsClient()

    def bind_context(self, context: AbsAppContext, **kwargs):
        self.context = context
    
    # ----------------    HANDLER    ----------------
    async def _get_handlers(self) -> Dict[str, AbsHandler]:
        pass

    async def process_message(self, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        handler: AbsHandler = self._handlers.get(message.msg_type)
        if handler:
            await handler.set_manager(self)
            await handler.handle_message(message, **kwargs)
        else:
            print(f'{self.__class__.__name__} not found handler for {message}')