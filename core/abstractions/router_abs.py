# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from .context_abs import AbsAppContext, AppContextValidator


class AbsRouter(ABC):
    context: AbsAppContext = AppContextValidator()
    @abstractmethod
    async def bind_context(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def process_message(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def run_check_data_message(self, *args, **kwargs):
        raise NotImplementedError
