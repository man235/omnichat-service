# -*- coding: utf-8 -*-
import asyncio
from functools import wraps
from typing import Sequence, Tuple
from django.conf import settings
from aioredis.sentinel import Sentinel
from aioredis.client import Pipeline, Redis, Lock
from aioredis.client import AnyFieldT, FieldT, EncodableT, GroupT
from aioredis.client import KeyT, KeysT, StreamIdT, ExpiryT, PatternT
from aioredis.exceptions import ConnectionError
from typing import Sequence, Tuple, Union, Any, Type, Dict, Mapping
from core.abstractions import SingletonClass
from core import constants


def reconnect(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        for i in range(3):
            try:
                return await func(self, *args, **kwargs)
            except (ConnectionError,) as e:
                print(f'get exception {e} try reconnect')
                await asyncio.sleep(3)
        # TODO: query fail after n times,
        #       should notify with highest priority
    return wrapper


class SentinelClient(SingletonClass):
    def _singleton_init(self, **kwargs):
        self.sentinel_namespace = settings.SENTINEL_NAMESPACE
        self.sentinel = None
        self.master_client: Redis = None
        self.slave_client: Redis = None

    def reset_client(self, **kwargs):
        self.initialize_sentinel()

    def initialize_sentinel(
        self, 
        sentinel_urls: Sequence[Tuple[str, int]] = settings.SENTINEL_URLS,
        sentinel_password: str = settings.SENTINEL_PASSWORD,
        sentinel_decode_response: bool = settings.SENTINEL_DECODE_RESPONSE,
        sentinel_db: int = settings.SENTINEL_DB,
        **kwargs
    ):
        self.sentinel: Sentinel = Sentinel(
            sentinel_urls,
            password=sentinel_password,
            decode_responses=sentinel_decode_response,
            db=sentinel_db
        )
        self.master_client: Redis = self.sentinel.master_for(self.sentinel_namespace)
        self.slave_client: Redis = self.sentinel.slave_for(self.sentinel_namespace)
        # self.master_client.hdel()
        # self.master_client.rpush()

    async def get_client(self, **kwargs) -> Redis:
        if kwargs.get(constants.SENTINEL_USE_SLAVE) and isinstance(self.slave_client, Redis):
            return self.slave_client
        return self.master_client

    @reconnect
    async def _execute(self, command: str, *args, **kwargs):
        if constants.SENTINEL_USE_SLAVE in kwargs:
            use_slave = kwargs.get(constants.SENTINEL_USE_SLAVE)
            del kwargs[constants.SENTINEL_USE_SLAVE]
        else:
            use_slave = False

        client = await self.get_client(use_slave)

        if hasattr(client, command) and callable(getattr(client, command)):
            return await getattr(client, command)(*args, **kwargs)
        raise ValueError(f'recheck client {client} command {command}')


    # ---------------------------------------------------------------
    #                       Methods for pipeline

    @reconnect
    async def pipeline(self, transaction: bool = True, shard_hint: str = None, **kwargs) -> Pipeline:
        client = await self.get_client(**kwargs)
        return client.pipeline(transaction, shard_hint)
    # End Methods for pipeline---------------------------------------

    # ---------------------------------------------------------------
    #                       Methods for INCR

    @reconnect
    async def incr(self, name: KeyT, amount: int = 1, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.incr(name, amount)

    @reconnect
    async def expire(self, name: KeyT, time: ExpiryT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.expire(name, time)

    # End Methods for pipeline---------------------------------------

    # ---------------------------------------------------------------
    #                       Methods for lock

    @reconnect
    async def lock(
        self,
        name: KeyT,                 # copy from aioredis
        timeout: float = None,      # copy from aioredis
        sleep: float = 0.1,         # copy from aioredis
        blocking_timeout: float = None,  # copy from aioredis
        lock_class: Type[Lock] = None,  # copy from aioredis
        thread_local=True,              # copy from aioredis
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        return client.lock(name, timeout, sleep, blocking_timeout, lock_class, thread_local)

    # ---------------------------------------------------------------
    #                       Methods for stream

    @reconnect
    async def xinfo_stream(self, name: KeyT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.xinfo_stream(name)

    @reconnect
    async def xadd(
        self,
        name: KeyT,
        fields: Dict[FieldT, EncodableT],
        id: StreamIdT = "*",
        maxlen: int = None,
        approximate: bool = True,
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        return await client.xadd(name, fields, id, maxlen, approximate)

    @reconnect
    async def xread(self, streams: Dict[KeyT, StreamIdT], count: int = None, block: int = None, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.xread(streams, count, block)

    @reconnect
    async def xreadgroup(
        self,
        groupname: str,
        consumername: str,
        streams: Dict[KeyT, StreamIdT],
        count: int = None,
        block: int = None,
        noack: bool = False,
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        return await client.xreadgroup(groupname, consumername, streams, count, block, noack)

    @reconnect
    async def xack(self, name: KeyT, groupname: GroupT, *ids: StreamIdT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.xack(name, groupname, *ids)

    # END------------------------------------------------------------

    # ---------------------------------------------------------------
    #                       Methods for get set type string

    @reconnect
    async def keys(self, pattern: PatternT = "*", **kwargs):
        client = await self.get_client(**kwargs)
        return await client.keys(pattern)

    @reconnect
    async def get(self, name: KeyT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.get(name)

    @reconnect
    async def set(
        self,
        name: KeyT,
        value: EncodableT,
        ex: ExpiryT = None,
        px: ExpiryT = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        return await client.set(name, value, ex, px, nx, xx, keepttl)

    @reconnect
    async def delete(
        self, *names: KeyT,
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        return await client.delete(*names)
    # END------------------------------------------------------------

    # ---------------------------------------------------------------
    #                       Methods for get set type hash

    @reconnect
    async def hget(self, name: KeyT, key: FieldT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.hget(name, key)

    @reconnect
    async def hgetall(self, name: KeyT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.hgetall(name)

    @reconnect
    async def hmget(self, name: KeyT, keys: Sequence[FieldT], **kwargs):
        client = await self.get_client(**kwargs)
        return await client.hmget(name, keys)

    @reconnect
    async def hset(
        self,
        name: KeyT,
        key: FieldT = None,
        value: EncodableT = None,
        mapping: Mapping[AnyFieldT, EncodableT] = None,
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        return await client.hset(name, key, value, mapping)

    @reconnect
    async def hdel(
        self,
        name: KeyT,
        *keys: FieldT,
        **kwargs
    ):
        client = await self.get_client(**kwargs)
        print('name', name)
        return await client.hdel(name, *keys)

    # END------------------------------------------------------------

    # ---------------------------------------------------------------
    #                       Methods for get set type list

    @reconnect
    async def lpush(self, name: KeyT, *values: EncodableT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.lpush(name, *values)

    @reconnect
    async def rpush(self, name: KeyT, *values: EncodableT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.rpush(name, *values)

    @reconnect
    async def lindex(self, name: KeyT, index: int, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.lindex(name, index)

    @reconnect
    async def linsert(self, name: KeyT, where: str, refvalue: EncodableT, value: EncodableT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.linsert(name, where, refvalue, value)

    @reconnect
    async def llen(self, name: KeyT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.llen(name)

    @reconnect
    async def lpop(self, name: KeyT, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.lpop(name)

    @reconnect
    async def lrange(self, name: KeyT, start: int, end: int, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.lrange(name, start, end)

    @reconnect
    async def lmove(self, source_name: KeyT, destination_name: KeyT, source_side: str, destination_side: str, **kwargs):
        for side in (source_side, destination_side,):
            if side.lower() not in ("left", 'right'):
                raise ValueError(f'source_side or destination_side must be string of "LEFT" or "RIGHT"')
        client = await self.get_client(**kwargs)
        return await client.execute_command("LMOVE", source_name, destination_name, source_side, destination_side)
    # END------------------------------------------------------------

    # ---------------------------------------------------------------
    #                       Methods for others

    @reconnect
    async def incr(self, name: KeyT, amount: int = 1, **kwargs):
        client = await self.get_client(**kwargs)
        return await client.incr(name, amount)

    # END------------------------------------------------------------
