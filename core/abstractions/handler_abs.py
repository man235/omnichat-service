from abc import ABC, abstractmethod


class AbsHandler(ABC):
    @abstractmethod
    async def handle_message(self, *args, **kwargs):
        raise NotImplementedError
    
    async def set_manager(self, *args, **kwargs):
        raise NotImplementedError
