from abc import ABC, abstractmethod
from .context_abs import AbsAppContext, AppContextValidator
from .validations_abs import AbsValidator


class AbsReceive(ABC):
    context: AbsAppContext = AppContextValidator()
    @abstractmethod
    def bind_context(self, context, **kwargs):
        raise NotImplementedError


class AbsCheckDataMessage(ABC):
    @abstractmethod
    async def check_data_message(self, *args, **kwargs):
        raise NotImplementedError
