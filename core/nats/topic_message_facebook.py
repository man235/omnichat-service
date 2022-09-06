import asyncio
import json
from django.conf import settings
from core.utils import save_message_store_database, check_room_facebook

from config.connect import nats_client

async def subscribe_handler(msg):
    data = json.loads((msg.data.decode("utf-8")).replace("'", "\""))
    room = await check_room_facebook(data)
    if not room:
        return      # No Fanpage to subscribe
    new_topic_publish = f'message_{room.room_id}'
    await nats_client.publish(new_topic_publish, bytes(msg.data))
    await save_message_store_database(data)

async def subscribe_channels(topics):
    # nc = await nats.connect(settings.NATS_URL)
    # await nc.connect(servers=[settings.NATS_URL])
    for topic in topics:
        await nats_client.subscribe(topic, "message", subscribe_handler)

async def main():
    topics = settings.CHANNELS_SUBSCRIBE
    await asyncio.gather(
        subscribe_channels(topics),
    )

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
