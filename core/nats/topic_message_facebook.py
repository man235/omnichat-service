import asyncio
import json
import uuid
from django.conf import settings
from core.utils import save_message_store_database, check_room_facebook, format_message_data_for_websocket
from core.context import AppContextManager
from core.schema import CoreChatInputMessage
from core import constants
from nats.aio.client import Client as NATS
nats_client = NATS()
import logging
logger = logging.getLogger(__name__)


async def subscribe_channels(topics):
    await nats_client.connect(servers=[settings.NATS_URL])
    logger.debug(f' natsUrl ----------------- {settings.NATS_URL} -------- ')

    app_context = AppContextManager()
    async def subscribe_handler(msg):
        try:
            data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
            data['_uuid'] = str(uuid.uuid4())
            logger.debug(f'data subscribe natsUrl ----------------- {data}')
            
            if not data.get('typeChat'):
                logger.debug(f'Data Receive not chat type -----------------')
                raise
            text_message = CoreChatInputMessage(msg_type=constants.MESSAGE_TEXT, chat_type=data.get('typeChat'))
            await app_context.run_receiver(text_message, data)
            logger.debug(f'RECEIVE DATA -----------------')
        except Exception as e:
            logger.debug(f'Exception subscribe ----------------- {e}')

    for topic in topics:
        await nats_client.subscribe(topic, "worker", subscribe_handler)
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
