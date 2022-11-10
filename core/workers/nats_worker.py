# -*- coding: utf-8 -*-
from .base import BaseWorker
import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union
import asyncio
import json
import uuid
from django.conf import settings
from core.context import AppContextManager
from core.schema import NatsChatMessage, FormatSendMessage
from core import constants
from pydantic import parse_obj_as, parse_raw_as
from nats.aio.client import Client as NATS
import logging

nats_client = NATS()
logger = logging.getLogger(__name__)


class NatsWorker(BaseWorker):
    worker_type = "nats_worker"

    def __init__(self, *args, **kwargs) -> None:
        self.__call__()
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        pass
    
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
        self.loop.run_forever()
    
    async def __call_wrapper(self):
        await self._run()
    
    async def _run(self):
        try:
            await self.run()
        except Exception as e:
            print("got exception -> ", e)

    async def subscribe_channels(self, topics):
        await nats_client.connect(servers=[settings.NATS_URL])
        logger.debug(f' natsUrl ----------------- {settings.NATS_URL} -------- ')

        app_context = AppContextManager()
        async def subscribe_handler(msg):
            try:
                nats_message = parse_raw_as(NatsChatMessage, (msg.data.decode("utf-8")).replace("'", "\""))
                nats_message.uuid = str(uuid.uuid4())
                logger.debug(f"{nats_message} ********************************************** ")
                await app_context.run_receiver(nats_message)
                logger.debug(f'RECEIVE DATA -----------------')
            except Exception as e:
                logger.debug(f'Exception subscribe ----------------- {e}')
        
        async def chat_message_to_corechat(msg):
            try:
                _message = parse_raw_as(FormatSendMessage, msg.data.decode("utf-8"))
                # data = json.loads(msg.data.decode("utf-8"))
                # _message = parse_obj_as(FormatSendMessage, data)
                logger.debug(f'RECEIVE DATA chat_message_to_corechat ------------------------------------------------------- {_message}')
                await app_context.run_send_message(_message)
            except Exception as e:
                logger.debug(f'Exception subscribe chat_message_to_corechat ----------------- {e}')

        await nats_client.subscribe(constants.WEBHOOK_TO_CORECHAT_MESSAGE, constants.WEBHOOK_TO_CORECHAT_MESSAGE, subscribe_handler)
        await nats_client.subscribe(constants.CHAT_SERVICE_TO_CORECHAT_SUBSCRIBE, constants.CHAT_SERVICE_TO_CORECHAT_SUBSCRIBE, chat_message_to_corechat)
        logger.debug(f'After Subscribe natsUrl --------------------------------------------------- ')


    async def run(self):
        logger.debug(f'data subscribe natsUrl ----------------- {nats_client} -------- {settings.NATS_URL}')
        topics = settings.CHANNELS_SUBSCRIBE
        await asyncio.gather(
            self.subscribe_channels(topics),
        )
