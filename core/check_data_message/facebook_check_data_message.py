from .base import BaseCheckDataMessageManager
from core import constants
from typing import Dict
from core.schema import CoreChatInputMessage
from core.utils import check_room_facebook


class CheckDataMessageFacebook(BaseCheckDataMessageManager):
    chat_type: str = constants.FACEBOOK

    async def check_data_message(self, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        room = await check_room_facebook(data)
        return room
