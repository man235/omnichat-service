# -*- coding: utf-8 -*-
from .base import BaseStreamClient


class RedisClient(BaseStreamClient):
    def __init__(self) -> None:
        super().__init__()

    async def connect(self, *args, **kwargs):
        return await super().connect(*args, **kwargs)

    async def disconnect(self, *args, **kwargs):
        return await super().disconnect(*args, **kwargs)

    async def publish(self, *args, **kwargs):
        return await super().publish(*args, **kwargs)

    async def subscribe(self, *args, **kwargs):
        return await super().subscribe(*args, **kwargs)
