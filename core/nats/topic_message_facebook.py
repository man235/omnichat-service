import asyncio
import json
from django.conf import settings
from core.utils import save_message_store_database, check_room_facebook, format_message_data_for_websocket
from nats.aio.client import Client as NATS
nats_client = NATS()
import logging
logger = logging.getLogger(__name__)


async def subscribe_channels(topics):
    await nats_client.connect(servers=[settings.NATS_URL])
    async def subscribe_handler(msg):
        try:
            logger.debug(f'data subscribe natsUrl ----------------- {msg.data}')
            data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
            room = await check_room_facebook(data)
            if not room:
                return      # No Fanpage to subscribe
            data_message = format_message_data_for_websocket(data)
            new_topic_publish = f'message_{room.room_id}'
            await nats_client.publish(new_topic_publish, data_message.encode())
            await save_message_store_database(room, data)
        except Exception as e:
            logger.debug(f'Exception subscribe ----------------- {e}')

    for topic in topics:
        await nats_client.subscribe(topic, "worker", subscribe_handler)
    logger.debug(f'After Subscribe natsUrl --------------------------------------------------- ')

async def main():
    logger.debug(f'data subscribe natsUrl ----------------- {nats_client} -------- ')
    topics = settings.CHANNELS_SUBSCRIBE
    # topics = "omniChat.message.receive.*"
    await asyncio.gather(
        subscribe_channels(topics),
    )

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
