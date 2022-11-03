# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class AbsWorker(ABC):
    @abstractmethod
    async def run(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def snapshot(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def restore(self, *args, **kwargs):
        raise NotImplementedError
