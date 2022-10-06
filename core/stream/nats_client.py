# -*- coding: utf-8 -*-
from typing import Callable, Union, List, Optional, Dict
from .base import BaseStreamClient
import nats
from django.conf import settings
from nats.errors import NoServersError, ConnectionClosedError, TimeoutError     # noqa


class NatsClient(BaseStreamClient):
    def __init__(self) -> None:
        self._client = None
        self._name = None

    async def connect(
        self,
        server_url: Union[str, List[str]] = [settings.NATS_URL],
        **kwargs
    ):
        if isinstance(self._client, nats.NATS) and self._client.is_connected:
            return

        self._client = await nats.connect(server_url, **kwargs)
        self._name = f'NATs-Client-{server_url}'
        print(self._client, self._client.is_connected)
        return self._client

    async def disconnect(self, *args, **kwargs):
        return await super().disconnect(*args, **kwargs)

    async def publish(
        self,
        subject: str,
        payload: bytes,
        reply: str = '',
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        if not self._client.is_connected:
            if kwargs.get('servers') and isinstance(kwargs.get('servers'), (str, list, )):
                await self.connect(kwargs.get('servers'))
            else:
                raise NoServersError

        return await self._client.publish(subject, payload, reply, headers)

    async def subscribe(
        self,
        subject: str,
        callback_func: Callable,
        **kwargs
    ):
        return await self._client.subscribe(subject, cb=callback_func)
