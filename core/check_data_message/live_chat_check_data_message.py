from typing import Dict
from core.schema.message_receive import NatsChatMessage
from core.utils.check_room_live_chat import check_room_live_chat
from .base import BaseCheckDataMessageManager
from core import constants


class CheckDataMessageLiveChat(BaseCheckDataMessageManager):
    chat_type: str = constants.LIVECHAT

    async def check_data_message(self, data: NatsChatMessage, *args, **kwargs):
        room = await check_room_live_chat(data)
        return room
