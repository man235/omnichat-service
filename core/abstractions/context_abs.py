from abc import ABC, abstractmethod
from .validations_abs import AbsValidator


class AbsAppContext(ABC):
    @abstractmethod
    async def run_receiver(self, *args, **kwargs):
        raise NotImplementedError    

    @abstractmethod
    async def run_send_message(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def run_manager(self, *args, **kwargs):
        raise NotImplementedError

    async def run_send_message_manager(self, *args, **kwargs):
        raise NotImplementedError


class AppContextValidator(AbsValidator):
    def __init__(self) -> None:
        self.default = None

    def validate(self, value):
        if not isinstance(value, AbsAppContext):
            raise TypeError(f'Expected {value!r} to be an instance of AbsAppContext')
