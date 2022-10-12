# -*- coding: utf-8 -*-
import inspect
from typing import Dict
from core.abstractions import AbsStreamClient, AbsStreamClientManager
from core.abstractions import SingletonClass


class BaseStreamClient(AbsStreamClient):
    _client = None
    _name = None

    @property
    def name(self, *args, **kwargs) -> str:
        return self._name

    @property
    def is_connected(self, *args, **kwargs) -> bool:
        return self._client.is_connected

    async def disconnect(self, *args, **kwargs):
        pass


class BaseStreamClientManager(SingletonClass, AbsStreamClientManager):
    def _singleton_init(self, clients: Dict[str, BaseStreamClient] = [], **kwargs):
        self._clients: Dict[str, BaseStreamClient] = {}
        for name, client in clients:

            if isinstance(client, BaseStreamClient):
                self._clients.update({name: client})

            if inspect.isclass(client) and issubclass(client, BaseStreamClient):
                self._clients.update({name: client()})

    async def publish_all(self, *args, **kwargs):
        for name, client in self._clients.items():
            if client.is_connected:
                await client.publish(*args, **kwargs)

    async def add_client(self, name: str, client: BaseStreamClient, **kwargs):
        if not isinstance(name, str) or not isinstance(client, BaseStreamClient):
            raise ValueError('expect name is string and client is an instance of BaseStreamClient')

        self._clients.update({name: client})
        print(f'added client {name} -> {client} -> is_connected {client.is_connected}')

    async def remove_client(self, name: str, **kwargs):
        if name in self._clients:
            del self._clients[name]

    async def disconnect_all(self, *args, **kwargs):
        for name, client in self._clients.items():
            await client.disconnect(*args, **kwargs)
