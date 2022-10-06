from .base import BaseCheckDataMessageManager
from core import constants
from typing import Dict
from core.schema import NatsChatMessage
from core.utils import check_room_facebook


class CheckDataMessageFacebook(BaseCheckDataMessageManager):
    chat_type: str = constants.FACEBOOK

    async def check_data_message(self, data: NatsChatMessage, *args, **kwargs):
        room = await check_room_facebook(data)
        return room
