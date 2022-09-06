import asyncio
import nats
from django.conf import settings


async def connect_nats_client():
    return await nats.connect(settings.NATS_URL)

nats_client = asyncio.get_event_loop().run_until_complete(connect_nats_client())