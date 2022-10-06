from abc import ABC, abstractmethod


class AbsHandler(ABC):
    @abstractmethod
    async def handle_message(self, *args, **kwargs):
        raise NotImplementedError
    
    async def get_manager(self, *args, **kwargs):
        raise NotImplementedError
