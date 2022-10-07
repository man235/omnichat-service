from .base import BaseHandler
from core import constants

class ZaloHandle(BaseHandler):
    htype: str = constants.ZALO

    async def handle_message(self, *args, **kwargs):
        print(f"{type(self).__name__} handle_message: ----------------------+--------= ")
        
