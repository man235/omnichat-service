# -*- coding: utf-8 -*-
import os
import uvloop
import asyncio
import random
from typing import Any, Callable, Dict, List, Optional, Set, Union
from core.abstractions import AbsWorker

uvloop.install()


class BaseWorker(AbsWorker):
    worker_type: str = 'base'


    def __init__(self, loop: uvloop.Loop = None, name: str = None) -> None:
        self.name: str = name or self._generate_worker_name()
        self.loop: uvloop.Loop = loop

    def _generate_worker_name(self) -> str:
        random_name = ''
        for i in range(10):
            random_name += chr(random.randint(97, 122))
        random_name = random_name.capitalize()
        return f'{self.worker_type}-{random_name}'

    async def _async_sleep(self, delay: float):
        sleep_task = asyncio.create_task(asyncio.sleep(delay))
        self._sleepers.add(sleep_task)
        try:
            await sleep_task
        except asyncio.CancelledError:
            pass
        finally:
            self._sleepers.remove(sleep_task)

    def _setup_loop(self, **kwargs):
        # create new loop
        try:
            self.loop = asyncio.get_running_loop()
        except:
            self.loop = asyncio.get_event_loop()
            pass
        print('worker loop id', self.loop, id(self.loop))

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._setup_loop()
        self.loop.run_until_complete(self.__call_wrapper())

    async def __call_wrapper(self):
        await self._run()

    async def _run(self):
        try:
            await self.run()
        except Exception as e:
            print("got exception -> ", e)

    async def run(self, *args, **kwargs):
        return

    async def snapshot(self, *args, **kwargs):
        return

    async def restore(self, *args, **kwargs):
        return
