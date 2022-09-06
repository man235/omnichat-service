import asyncio
from django.conf import settings
from core.utils import save_message_store_database, check_room_facebook

# channel = redis_client.pubsub()

async def publish_channels(channels):
    # def event_handler(msg):
    #     print('Handler', msg)
    for topic in channels:
        try:
            check_pub_sub = redis_client.pubsub_numsub(topic)
            if check_pub_sub[0][1] == 1:
                # channel.psubscribe(**{topic: event_handler})
                channel.psubscribe(topic)
                continue
            channel.subscribe(topic)
        except Exception as e:
            print(f"Exception subscribe channel: {e}")

    for publish in channel.listen():
        try:
            if isinstance(publish.get('data'), int):
                pass
            else:
                data = bytes(publish.get('data'))
                new_topic_publish = 'message_17662229160485412'
                redis_client.publish(new_topic_publish, "Thienhi")
                pass
        except Exception as e:
            print(f"Exception publish message: {e}")

async def main():
    channels = settings.CHANNELS_SUBSCRIBE
    asyncio.gather(
        publish_channels(channels),
    )

# asyncio.get_event_loop().run_until_complete(main())
# asyncio.get_event_loop().run_forever()
