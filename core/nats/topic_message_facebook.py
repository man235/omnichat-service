import asyncio
import json
import uuid
from django.conf import settings
from core.context import AppContextManager
from core.schema import CoreChatInputMessage, NatsChatMessage, FormatSendMessage
from core import constants
from pydantic import BaseModel, parse_obj_as
from nats.aio.client import Client as NATS
import logging

nats_client = NATS()
logger = logging.getLogger(__name__)


async def subscribe_channels(topics):
    await nats_client.connect(servers=[settings.NATS_URL])
    logger.debug(f' natsUrl ----------------- {settings.NATS_URL} -------- ')

    app_context = AppContextManager()
    async def subscribe_handler(msg):
        try:
            data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
            data['uuid'] = str(uuid.uuid4())
            nats_message = parse_obj_as(NatsChatMessage, data)
            logger.debug(f' nats_message ----------------- {data} -------- {nats_message}')
            if not nats_message.typeChat:
                logger.debug(f'Data Receive not chat type')
                return
            text_message = CoreChatInputMessage(msg_type=constants.MESSAGE_TEXT, chat_type=data.get('typeChat'))
            await app_context.run_receiver(text_message, nats_message)
            logger.debug(f'RECEIVE DATA -----------------')
        except Exception as e:
            logger.debug(f'Exception subscribe ----------------- {e}')
    
    async def chat_message_to_corechat(msg):
        try:
            data = json.loads(msg.data.decode("utf-8"))
            _message = parse_obj_as(FormatSendMessage, data)
            logger.debug(f'RECEIVE DATA chat_message_to_corechat ------------------------------------------------------- {_message}')
            await app_context.run_send_message(_message)
        except Exception as e:
            logger.debug(f'Exception subscribe chat_message_to_corechat ----------------- {e}')

    # for topic in topics:
    #     await nats_client.subscribe(topic, topic, subscribe_handler)
    await nats_client.subscribe(constants.WEBHOOK_TO_CORECHAT_MESSAGE, constants.WEBHOOK_TO_CORECHAT_MESSAGE, subscribe_handler)
    await nats_client.subscribe(constants.CHAT_SERVICE_TO_CORECHAT_SUBSCRIBE, constants.CHAT_SERVICE_TO_CORECHAT_SUBSCRIBE, chat_message_to_corechat)
    logger.debug(f'After Subscribe natsUrl --------------------------------------------------- ')

async def main():
    logger.debug(f'data subscribe natsUrl ----------------- {nats_client} -------- {settings.NATS_URL}')
    topics = settings.CHANNELS_SUBSCRIBE
    # topics = "omniChat.message.receive.*"
    await asyncio.gather(
        subscribe_channels(topics),
    )

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
