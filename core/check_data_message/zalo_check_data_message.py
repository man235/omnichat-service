from .base import BaseCheckDataMessageManager
from core import constants
from typing import Dict
from core.schema import CoreChatInputMessage
from sop_chat_service.zalo.utils import check_room_zalo

class CheckDataMessageZalo(BaseCheckDataMessageManager):
    chat_type: str = constants.ZALO

    async def check_data_message(self, message: CoreChatInputMessage, data: Dict, *args, **kwargs):
        room = await check_room_zalo(data)
        return room
