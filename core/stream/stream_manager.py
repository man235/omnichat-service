# -*- coding: utf-8 -*-
import nats
from typing import List
from .base import BaseStreamClient
from .base import BaseStreamClientManager


class StreamClientManager(BaseStreamClientManager):
    '''
    Add a stream client
        client = StreamClient(NatsClient)
        await client.connect(settings.get_nats_serveres())

    '''

    async def get_all_nats_clients(self) -> List[BaseStreamClient]:
        print(self._clients)
        return [client for name, client in self._clients.items() if isinstance(client._client, nats.NATS)]

    async def publish_nats_all_clients(self,  *args, **kwargs):
        _result = {}
        for name, client in self._clients.items():
            if isinstance(client._client, nats.NATS):
                if client.is_connected:
                    res = await client.publish(*args, **kwargs)
                    _result.update({'client': name, 'publish_res': res})
        return _result
