import asyncio
import json
from django.conf import settings
from core.utils import save_message_store_database, check_room_facebook
# from config.connect import nats_client
from sop_chat_service.app_connect.models import FanPage
from nats.aio.client import Client as NATS
nats_client = NATS()
import logging
logger = logging.getLogger(__name__)


async def subscribe_handler(msg):
    data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
    logger.debug(f'data subscribe natsUrl ----------------- {data}')
    room = await check_room_facebook(data)
    if not room:
        return      # No Fanpage to subscribe
    new_topic_publish = f'message_{room.room_id}'
    await nats_client.publish(new_topic_publish, bytes(msg.data))
    await save_message_store_database(room, data)

async def subscribe_channels(topics):
    await nats_client.connect(servers=[settings.NATS_URL])
    all_fanpage = FanPage.objects.all()
    for fanpage in all_fanpage:
        topic = topics+fanpage.page_id
        logger.debug(f'Before Subscribe natsUrl --------------------------------------------------- ')
        await nats_client.subscribe(topic, "worker", subscribe_handler)
        logger.debug(f'After Subscribe natsUrl --------------------------------------------------- ')

async def main():
    logger.debug(f'data subscribe natsUrl ----------------- {settings.CHANNELS_SUBSCRIBE}')
    # topics = settings.CHANNELS_SUBSCRIBE
    topics = "omniChat.message.receive."
    await asyncio.gather(
        subscribe_channels(topics),
    )

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
