# from .base import BaseWebSocketHandler
from core import constants
from core.schema import CoreChatInputMessage
from core.handlers import BaseHandler

class LiveChatWebSocketHandler(BaseHandler):
    ws_type: str = constants.LIVECHAT

    async def handle_message(self, message: CoreChatInputMessage, *args, **kwargs):
        print("LiveChatWebSocketHandler handle_message_websocket: ----------------------+--------= ", self.ws_type)
        pass
