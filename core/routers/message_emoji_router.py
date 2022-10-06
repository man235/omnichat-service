from .base import BaseRouter
from core.schema import CoreChatInputMessage


class MessageEmojiRouter(BaseRouter):
    msg_type: str = 'emoji'
    
    async def process_message(self, message: CoreChatInputMessage, *args, **kwargs):
        pass
