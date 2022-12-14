from .base import BaseCheckDataMessageManager
from core import constants
from typing import Dict
from core.schema import NatsChatMessage
from sop_chat_service.zalo.utils import distribute_new_room_zalo

class CheckDataMessageZalo(BaseCheckDataMessageManager):
    chat_type: str = constants.ZALO

    async def check_data_message(self, data: NatsChatMessage, *args, **kwargs):
        # room = await check_room_zalo(data)
        room = await distribute_new_room_zalo(data)
        return room
