# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class AbsStreamClient(ABC):

    @property
    @abstractmethod
    async def name(self, *args, **kwargs) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_connected(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def connect(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def publish(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self, *args, **kwargs):
        raise NotImplementedError


class AbsStreamClientManager(ABC):
    @abstractmethod
    async def publish_all(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def add_client(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def remove_client(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def disconnect_all(self, *args, **kwargs):
        raise NotImplementedError
