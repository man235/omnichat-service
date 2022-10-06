from .base import BaseCheckDataMessageManager
from core import constants


class CheckDataMessageLiveChat(BaseCheckDataMessageManager):
    chat_type: str = constants.LIVECHAT

    async def check_data_message(self, *args, **kwargs):
        print("Check Data Message Live Chat: ----------------------+======== ")
