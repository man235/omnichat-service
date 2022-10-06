from typing import Dict
from core.abstractions.handler_abs import AbsHandler
from core.abstractions import SingletonClass

class BaseHandler(SingletonClass, AbsHandler):
    storage_type = None

    def _singleton_init(self, **kwargs):
        self._initialized: bool = False
    
    async def set_manager(self, manager):
        self.manager = manager

    async def handle_message(self, *args, **kwargs):
        print("BaseHandler run_storage: ----------------------")
