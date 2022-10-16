# -*- coding: utf-8 -*-
from typing import Callable, Union, List, Optional, Dict
from .base import BaseStreamClient
import nats
from core import constants
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
        # return await super().disconnect(*args, **kwargs)
        return await self._client.close()

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

    async def publish_message_from_corechat_to_websocket_facebook(
        self,
        room_id: str,
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
        subject = f"{constants.CORECHAT_TO_WEBSOCKET_FACEBOOK}.{room_id}"
        return await self._client.publish(subject, payload, reply, headers)

    async def publish_message_from_corechat_to_websocket_zalo(
        self,
        room_id: str,
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
        subject = f"{constants.CORECHAT_TO_WEBSOCKET_ZALO}.{room_id}"
        return await self._client.publish(subject, payload, reply, headers)

    async def publish_message_from_corechat_to_websocket_livechat(
        self,
        room_id: str,
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
        subject = f"{constants.CORECHAT_TO_WEBSOCKET_LIVECHAT}.{room_id}"
        return await self._client.publish(subject, payload, reply, headers)

    async def publish_message_from_corechat_to_webhook_livechat(
        self,
        room_id: str,
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
        subject = f"{constants.CORECHAT_TO_WEBHOOK_LIVECHAT}.{room_id}"
        return await self._client.publish(subject, payload, reply, headers)
