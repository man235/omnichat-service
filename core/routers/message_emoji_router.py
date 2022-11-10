from .base import BaseRouter

class MessageEmojiRouter(BaseRouter):
    msg_type: str = 'emoji'
    
    async def process_message(self, *args, **kwargs):
        pass
